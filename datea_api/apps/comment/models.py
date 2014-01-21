from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.html import strip_tags
from django.conf import settings


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

    def get_resource_class(self):
        return datea_api.apps.comment.resources.CommentResource
    
    def __unicode__(self):
        return self.user.username+': '+strip_tags(self.comment)[:25]
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')    

    

