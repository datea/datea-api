from django.core.management.base import BaseCommand, CommandError
from campaign.models import Campaign
from tag.models import Tag
from os.path import isfile
from django.core.paginator import Paginator
import math
from django.utils import timezone

class Command(BaseCommand):
    help  = "Do ranking for tags and campaigns"

    def add_arguments(self, parser):
        parser.add_argument('--limit', action='store', dest='limit', default=False, help='Delete poll instead of closing it')

    def handle(self, *args, **options) :

        limit = options['limit'] if options['limit'] else 10 # 10 Campaigns and 10 Tags

        if limit != 'all':
            limit = int(limit)
            if isfile('/tmp/datea-ranking-start.txt'):
                f = open('/tmp/datea-ranking-start.txt')
                start = [int(s) for s in f.read().split(',')]
            else:
                start = [0,0]

        # Process campaigns
        campaigns = Campaign.objects.all().order_by('-created')
        num_campaigns = campaigns.count()

        if limit != 'all':
            c_start = start[0]
            c_end = c_start + limit
            if c_end >= num_campaigns and num_campaigns > limit:
                c_end = num_campaigns - c_end - 1
            campaigns = campaigns[c_start : c_end]
            if c_end < 0:
                start[0] = -c_end - 1
            else:
                start[0] = c_end

        for camp in campaigns:
            rank = getScore(camp)
            camp.rank = rank
            camp.save()
            print 'processed campaign:', camp.name, rank

        # PROCESS TAGS
        tags = Tag.objects.all().order_by('-created')
        num_tags = tags.count()
        if limit != 'all':
            t_start = start[1]
            t_end = t_start + limit
            if t_end >= num_tags and num_tags > limit:
                t_end = num_tags - t_end - 1
            tags = tags[t_start : t_end]
            if t_end < 0:
                start[1] = -t_end - 1
            else:
                start[1] = t_end

        for tag in tags:
            rank = getScore(tag)
            tag.rank = rank
            tag.save()
            print 'processed tag:', tag.tag, rank

        if limit != 'all':
            f = open('/tmp/datea-ranking-start.txt', 'w')
            f.write(",".join([str(s) for s in start]))
            f.close()


def getScore(obj):
    today = timezone.now()
    score = 0
    for d in obj.dateos.filter(published=True):
        score += getDateoScore((today - d.created).days)
    return score


def getDateoScore(days_since_today):
    return math.log(5, days_since_today+5)
