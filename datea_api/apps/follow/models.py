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
    
    def save(self, *args, **kwargs):
        # update follow stats on voted object  
        if self.pk == None:
            receiver_obj = self.followed_object
            if hasattr(receiver_obj, 'follow_count'):
            	receiver_obj.follow_count += 1
            	receiver_obj.save()

        if not self.object_type:
            self.object_type = self.content_type.name

        super(Follow, self).save(*args, **kwargs)
       
        
    def delete(self, using=None):
        # update comment stats on voted object 
        #ctype = ContentType.objects.get(model=self.object_type.lower())
        receiver_obj = self.content_type.get_object_for_this_type(pk=self.object_id)
        if hasattr(receiver_obj, 'follow_count'):
            receiver_obj.follow_count -= 1
            receiver_obj.save()
        super(DateaFollow, self).delete(using=using)
    
    class Meta:
        verbose_name = _('Follow')
        verbose_name_plural = _('Follows')
        
    
 

