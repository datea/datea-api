from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


from django.conf import settings

"""
from django.db.models.signals import post_save, pre_delete, m2m_changed

from datea.datea_comment.models import DateaComment
from datea.datea_vote.models import DateaVote
from datea.datea_mapping.models import DateaMapping, DateaMapItem, DateaMapItemResponse
from datea.datea_mapping.signals import map_item_response_created
"""

class Follow(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="follows")
    created = models.DateTimeField(_('created'), auto_now_add=True)
    
    # generic content type relation to followed object
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField()

    #object_type = models.CharField(max_length=255)
    
    # a sort of natural key by which easily and rapidly 
    # identify the followed object and it's related historyNotices
    # for example: 'dateo.15'
    follow_key = models.CharField(max_length=255)
    published = models.BooleanField(default=True)

    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs): 
        if not self.follow_key:
            self.follow_key = self.content_type.model+'.'+str(self.object_id)
        super(Follow, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.follow_key


    class Meta:
        verbose_name = _('Follow')
        verbose_name_plural = _('Follows')




####
#  UPDATE STATS
#  better implemented with signals, if you'd like to turn this off.
#  updating stats on objects is done using celery
###
from django.db.models.signals import post_save, pre_delete
from follow.tasks import update_follow_stats 

def follow_saved(sender, instance, created, **kwargs):
    if created:
        update_follow_stats.delay(instance.content_type.model, instance.object_id, 1)

def follow_pre_delete(sender, instance, **kwargs):
    update_follow_stats.delay(instance.content_type.model, instance.object_id, -1)

post_save.connect(follow_saved, sender=Follow)
pre_delete.connect(follow_pre_delete, sender=Follow)
        
    
 

