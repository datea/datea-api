from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from dateo.search_indexes import DateoIndex
from django.db.models.signals import pre_delete, post_save
from notify.models import ActivityLog


class Vote(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes")
    
    created = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(default=1)
    
    # generic content type relation to voted object
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    vote_key = models.CharField(max_length=255, blank=True, null=True)

    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # something here
        if not self.vote_key:
            self.vote_key = self.content_type.model+'.'+str(self.object_id)
        elif (not self.object_id or not self.content_type) and self.vote_key:
            model, pk = self.vote_key.split('.')
            self.content_type = ContentType.objects.get(model=model)
            self.object_id = int(pk)  
        super(Vote, self).save(*args, **kwargs)

    def update_stats(self, value):

        if hasattr(self.content_object, 'vote_count'):
            self.content_object.vote_count += value
            self.content_object.save()

        if hasattr(self.content_object, 'user') and hasattr(self.content_object.user, 'voted_count'):
            self.content_object.user.voted_count += value
            self.content_object.user.save()

    
    def __unicode__(self):
        return "Vote "+self.user.username+" "+self.content_type.model+"."+str(self.object_id)

    class Meta:
        unique_together = ("user", "content_type", "object_id")


# UPDATE STATS
def after_vote_saved(sender, instance, created, **kwargs):
    if created:
        instance.update_stats(1)
        if (instance.content_type.model == 'dateo'):
            DateoIndex().update_object(instance.content_object)


def before_vote_delete(sender, instance, **kwargs):
    instance.update_stats(-1)
    ActivityLog.objects.filter(action_key='vote.'+str(instance.pk)).delete()
    if (instance.content_type.model == 'dateo'):
        DateoIndex().update_object(instance.content_object)

post_save.connect(after_vote_saved, sender=Vote, dispatch_uid="vote.saved")
pre_delete.connect(before_vote_delete, sender=Vote, dispatch_uid="vote.delete")

    

