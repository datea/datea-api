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
    
    # provide a way to know if published was changed
    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.__orig_published = self.published
    

    def save(self, *args, **kwargs):
        self.is_new = self.pk is None
        self.published_changed = self.__orig_published != self.published
        #update_comment_stats.delay(self)
        super(Comment, self).save(*args, **kwargs)
        
    
    def delete(self, using=None):
        self.is_new = self.pk is None
        self.published_changed = self.__orig_published != self.published
        #update_comment_stats.delay(self, 'delete')
        super(Comment, self).delete(using=using)
    
    def __unicode__(self):
        return self.user.username+': '+strip_tags(self.comment)[:25]
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        

# connect signal handlers
"""
from datea_api.apps.dateo.models import Dateo
from django.db.models.signals import pre_delete

def on_dateo_delete(sender, instance, **kwargs):
    # delete comments
    Comment.objects.filter(object_type__name='dateo', object_id=instance.id).delete()

pre_delete.connect(on_dateo_delete, sender=Dateo)
"""     

    

