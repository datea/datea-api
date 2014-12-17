from django.core.management.base import BaseCommand, CommandError
from datea_api.apps.dateo.models import Dateo
from datea_api.apps.account.models import User
from datea_api.apps.campaign.models import Campaign
from datea_api.apps.tag.models import Tag
from datea_api.apps.follow.models import Follow
from datea_api.apps.vote.models import Vote
from datea_api.apps.comment.models import Comment

class Command(BaseCommand):
	help = "fix counters of datea's objects"

	def handle(self, *args, **options):
		
		# Fix Dateo stats
		for d in Dateo.objects.all():
			# comments
			d.comment_count = Comment.objects.filter(content_type__model="dateo", object_id=d.pk).count()
			# votes
			d.vote_count = Vote.objects.filter(content_type__model="dateo", object_id=d.pk).count()
			d.save()

		# Fix User stats
		for u in User.objects.all():
			u.dateo_count = Dateo.objects.filter(user=u).count()
			
			votes = 0	
			for d in Dateo.objects.filter(user=u):
				votes += d.vote_count

			u.voted_count = votes
			u.save()

		# Fix campaign stats
		# only for main tags
		for c in Campaign.objects.all():
			c.dateo_count = Dateo.objects.filter(tags=c.main_tag).count()
			c.follow_count = Follow.objects.filter(content_type__model="tag", object_id=c.main_tag.pk).count()
			comments = 0
			for d in Dateo.objects.filter(tags=c.main_tag):
				comments += d.comment_count
			c.comment_count = comments
			c.save()

		# tag stats
		for t in Tag.objects.all():
			tdateos =  t.dateos.filter(published=True)
			t.dateo_count = tdateos.count()
			t.follow_count = Follow.objects.filter(follow_key='tag.'+str(t.pk)).count()

			img_count = 0
			for d in tdateos:
				img_count += d.images.count()
			t.image_count = img_count
			t.save()


		self.stdout.write("counters fixed")	
