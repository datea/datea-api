from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.html import strip_tags
from django.conf import settings
from campaign.models import Campaign
from django.core.cache import cache
from dateo.search_indexes import DateoIndex
from django.db.models.signals import pre_delete, post_save, pre_save
from notify.models import ActivityLog


class Comment(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'), related_name='comments')
    created = models.DateTimeField(_('created'), auto_now_add=True)
    comment = models.TextField(_('Comment'))
    reply_to = models.ForeignKey('self', null=True, blank=True, related_name="replies")
    published = models.BooleanField(default=True)
    
    # generic content type relation to commented object
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # do we need content type relation? perhaps this is more simple and fast...
    #object_type = models.CharField(_('Object Name'), max_length=50) # object typeid -> whatever
    object_id = models.PositiveIntegerField(_('Object id')) # object id

    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

    def get_resource_class(self):
        return comment.resources.CommentResource

    def update_stats(self, value):
        if hasattr(self.content_object, 'comment_count'):
            self.content_object.comment_count += value
            self.content_object.save()

        if hasattr(self.content_object, 'tags') and self.content_object.tags.count() > 0:
            campaigns = Campaign.objects.filter(main_tag__in=self.content_object.tags.all())
            for c in campaigns:
                if hasattr(c, 'comment_count'):
                    c.comment_count += value
                    c.save()
    
    def __unicode__(self):
        return self.user.username+': '+strip_tags(self.comment)[:25]
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')    


# UPDATE COMMENT STATS
def before_comment_saved(sender, instance, **kwargs):
    if (instance.content_type.model == 'dateo'):
        cache.delete('dateo.'+str(instance.object_id))


def after_comment_saved(sender, instance, created, **kwargs):
    if created:
        instance.update_stats(1)
        if (instance.content_type.model == 'dateo'):
            DateoIndex().update_object(instance.content_object)


def before_comment_delete(sender, instance, **kwargs):
    instance.update_stats(-1)
    ActivityLog.objects.filter(action_key='comment.'+str(instance.pk)).delete()
    if (instance.content_type.model == 'dateo'):
        DateoIndex().update_object(instance.content_object)

post_save.connect(after_comment_saved, sender=Comment, dispatch_uid="comment.saved")
pre_save.connect(before_comment_saved, sender=Comment, dispatch_uid="comment.pre_saved")
pre_delete.connect(before_comment_delete, sender=Comment, dispatch_uid="comment.delete")

