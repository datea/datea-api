from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.db.models.signals import post_init, post_save, pre_delete
from .tasks import do_vote_async_tasks


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

    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # update comment stats on voted object  
        super(Vote, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return _("Vote")



####
#  ASYNC ACTIONS WITH CELERY
#  better implemented with signals, if you'd like to turn this off.
#  updating stats, creating activity stream and sending notifications 
#  on objects is done using celery
###
def vote_saved(sender, instance, created, **kwargs):
    if created:
        do_vote_async_tasks.delay(instance.pk, 1)

def vote_pre_delete(sender, instance, **kwargs):
    do_vote_async_tasks.delay(instance.pk, -1, False)

post_save.connect(vote_saved, sender=Vote)
pre_delete.connect(vote_pre_delete, sender=Vote)
    

