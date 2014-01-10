from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.html import strip_tags

from django.conf import settings
from tasks import update_comment_stats
# Create your models here.


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
    
    def __unicode__(self):
        return self.user.username+': '+strip_tags(self.comment)[:25]
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        


####
#  UPDATE STATS
#  better implemented with signals, if you'd like to turn this off.
#  updating stats on objects is done using celery
###
from django.db.models.signals import post_init, post_save, pre_delete
from comment.tasks import update_comment_stats 

def comment_pre_saved(sender, instance, **kwargs):
    instance.__orig_published = instance.published

def comment_saved(sender, instance, created, **kwargs):
    instance.publish_changed = instance.__orig_published != instance.published
    value = 0
    if created and instance.published:
        value = 1
    elif not created and instance.publish_changed and instance.published:
        value = 1
    elif not created and instance.publish_changed and not instance.published:
        value = -1

    if value != 0:
        update_comment_stats.delay(instance.content_type.model, instance.object_id, value)

def comment_pre_delete(sender, instance, **kwargs):
    if instance.published:
        update_comment_stats(instance.content_type.model, instance.object_id, -1)

post_init.connect(comment_pre_saved, sender=Comment)
post_save.connect(comment_saved, sender=Comment)
pre_delete.connect(comment_pre_delete, sender=Comment)    

    

