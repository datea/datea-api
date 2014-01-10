from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Vote(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes")
    
    created = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(default=1)
    
    # generic content type relation to voted object
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    #object_type = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        # update comment stats on voted object  
        super(Vote, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return _("Vote")



####
#  UPDATE STATS
#  better implemented with signals, if you'd like to turn this off.
#  updating stats on objects is done using celery
###
from django.db.models.signals import post_init, post_save, pre_delete
from vote.tasks import update_vote_stats 

def vote_saved(sender, instance, created, **kwargs):
    if created:
        update_vote_stats.delay(instance.content_type.model, instance.object_id, 1)

def vote_pre_delete(sender, instance, **kwargs):
    update_dateo_stats.delay(instance.content_type.model, instance.object_id, -1)

post_save.connect(vote_saved, sender=Vote)
pre_delete.connect(vote_pre_delete, sender=Vote)
    

