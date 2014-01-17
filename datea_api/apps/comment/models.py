from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.html import strip_tags

from django.conf import settings
from django.db.models.signals import post_init, post_save, pre_delete
import comment.tasks


class Comment(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='comments')
    created = models.DateTimeField(_('created'), auto_now_add=True)
    comment = models.TextField(_('Comment'))
    reply_to = models.ForeignKey('self', null=True, blank=True, related_name="replies")
    published = models.BooleanField(default=True)
    
    # generic content type relation to commented object
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    # do we need content type relation? perhaps this is more simple and fast...
    #object_type = models.CharField(_('Object Name'), max_length=50) # object typeid -> whatever
    object_id = models.PositiveIntegerField(_('Object id')) # object id

    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)
    
    def __unicode__(self):
        return self.user.username+': '+strip_tags(self.comment)[:25]
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        

####
#  ASYNC ACTIONS WITH CELERY
#  better implemented with signals, if you'd like to turn this off.
#  updating stats, creating activity stream and sending notifications 
#  on objects is done using celery
###
 
def comment_pre_saved(sender, instance, **kwargs):
    instance.__orig_published = instance.published


def comment_saved(sender, instance, created, **kwargs):
    instance.publish_changed = instance.__orig_published != instance.published
    value = 0
    notify = False
    if created and instance.published:
        value = 1
        notify = True
    elif not created and instance.publish_changed and instance.published:
        value = 1
    elif not created and instance.publish_changed and not instance.published:
        value = -1

    if value != 0:
        comment.tasks.do_comment_async_tasks.delay(instance.pk, value, notify)


def comment_pre_delete(sender, instance, **kwargs):
    if instance.published:
        comment.tasks.do_comment_async_tasks(instance.pk, -1, False)

post_init.connect(comment_pre_saved, sender=Comment)
post_save.connect(comment_saved, sender=Comment)
pre_delete.connect(comment_pre_delete, sender=Comment)    

    

