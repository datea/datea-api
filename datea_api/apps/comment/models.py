from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.html import strip_tags

from django.conf import settings
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
    # object_type = models.CharField(_('Object Name'), max_length=50) # object typeid -> whatever
    object_id = models.PositiveIntegerField(_('Object id')) # object id
    
    # provide a way to know if published was changed
    def __init__(self, *args, **kwargs):
        super(DateaComment, self).__init__(*args, **kwargs)
        self.__orig_published = self.published
    

    def save(self, *args, **kwargs):
        self.update_stats()
        '''
        ctype = ContentType.objects.get(model=self.object_type.lower())
        receiver_obj = ctype.get_object_for_this_type(pk=self.object_id)
        if self.content_object != receiver_obj:
            self.content_object = receiver_obj
        '''
        super(DateaComment, self).save(*args, **kwargs)
        
    
    def delete(self, using=None):
        self.delete_stats()
        super(DateaComment, self).delete(using=using)
        
    
    def update_stats(self):
        ctype = ContentType.objects.get(model=self.object_type.lower())
        receiver_obj = self.content_object

        value = 0
        if ((self.pk == None and self.published)
          or (self.__orig_published == False and self.published and self.pk)): 
            value = 1
        elif (self.pk and self.published == False and self.__orig_published):
            value = -1
        
        if value != 0:
            prof = self.user.get_profile()
            prof.comment_count += value 
            prof.save() 
            
            if hasattr(receiver_obj, 'comment_count'):
                receiver_obj.comment_count += value
                receiver_obj.save()
            
            if hasattr(receiver_obj, 'action'):
                receiver_obj.action.comment_count += value
                receiver_obj.action.save()
    
    def delete_stats(self):
        if self.published and self.__orig_published:
            prof = self.user.get_profile()
            prof.comment_count -= 1
            prof.save() 
            
            ctype = ContentType.objects.get(model=self.object_type.lower())
            receiver_obj = ctype.get_object_for_this_type(pk=self.object_id)
            if hasattr(receiver_obj, 'comment_count'):
                receiver_obj.comment_count -= 1
                receiver_obj.save()
            if hasattr(receiver_obj, 'action'):
                receiver_obj.action.comment_count -= 1
                receiver_obj.action.save()
    
    def __unicode__(self):
        return self.user.username+': '+strip_tags(self.comment)[:25]
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        

# connect signal handlers
from datea_api.apps.dateo.models import Dateo
from django.db.models.signals import pre_delete

def on_dateo_delete(sender, instance, **kwargs):
    # delete comments
    Comment.objects.filter(object_type__name='dateo', object_id=instance.id).delete()

pre_delete.connect(on_dateo_delete, sender=Dateo)
        

    

