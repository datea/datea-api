from django.db import models
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from campaign.models import Campaign
from campaign.search_indexes import CampaignIndex
from django.core.cache import cache
from django.db.models.signals import pre_delete, post_save
from api.signals import resource_saved

class Follow(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="follows")
    created = models.DateTimeField('created', auto_now_add=True)

    # generic content type relation to followed object
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField(null=True, blank=True)

    # a sort of natural key by which easily and rapidly
    # identify the followed object and it's related historyNotices
    # for example: 'dateo.15'
    follow_key = models.CharField(max_length=255)
    published = models.BooleanField(default=True)

    client_domain = models.CharField('CLient Domain', max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.follow_key:
            self.follow_key = self.content_type.model+'.'+str(self.object_id)
        elif (not self.content_type or not self.object_id) and self.follow_key:
            model, pk = self.follow_key.split('.')
            self.content_type = ContentType.objects.get(model=model)
            self.object_id = int(pk)

        super(Follow, self).save(*args, **kwargs)


    def update_stats(self, value):
        if hasattr(self.content_object, 'follow_count'):
            self.content_object.follow_count += value
            self.content_object.save()

        if self.content_type.model == 'tag':
            campaigns = Campaign.objects.filter(main_tag=self.content_object)
            for c in campaigns:
                if hasattr(c, 'follow_count'):
                    c.follow_count += value
                    c.save()
                    CampaignIndex().update_object(c)
                    cache.delete('campaign.'+str(c.pk))


    def __unicode__(self):
        return self.user.username+": "+self.follow_key

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        unique_together = ("user", "follow_key")


####
#  UPDATE STATS
#  better implemented with signals, if you'd like to turn this off.
#  updating stats on objects is done using celery
###

def follow_saved(sender, instance, created, **kwargs):
    if created:
        instance.update_stats(1)

def follow_pre_delete(sender, instance, **kwargs):
    instance.update_stats(-1)

post_save.connect(follow_saved, sender=Follow, dispatch_uid="follow.save")
pre_delete.connect(follow_pre_delete, sender=Follow, dispatch_uid="follow.delete")
