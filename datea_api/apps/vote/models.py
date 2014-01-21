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

    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # update comment stats on voted object  
        super(Vote, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return "Vote "+self.user.username+" "+self.content_type.model+"."+str(self.object_id)

    class Meta:
        unique_together = ("user", "content_type", "object_id")

    

