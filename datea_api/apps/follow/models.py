from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings


class Follow(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="follows")
    created = models.DateTimeField(_('created'), auto_now_add=True)
    
    # generic content type relation to followed object
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField(null=True, blank=True)

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
        elif (not self.content_type or not self.object_id) and self.follow_key:
            model, pk = self.follow_key.split('.')
            self.content_type = ContentType.objects.get(model=model)
            self.object_id = int(pk)

        super(Follow, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.follow_key


    class Meta:
        verbose_name = _('Follow')
        verbose_name_plural = _('Follows')
        unique_together = ("user", "follow_key")




####
#  UPDATE STATS
#  better implemented with signals, if you'd like to turn this off.
#  updating stats on objects is done using celery
###
from django.db.models.signals import post_save, pre_delete
from .tasks import update_follow_stats 

def follow_saved(sender, instance, created, **kwargs):
    if created:
        update_follow_stats.delay(instance.content_type.model, instance.object_id, 1)

def follow_pre_delete(sender, instance, **kwargs):
    update_follow_stats.delay(instance.content_type.model, instance.object_id, -1)

post_save.connect(follow_saved, sender=Follow)
pre_delete.connect(follow_pre_delete, sender=Follow)
        
    
 

