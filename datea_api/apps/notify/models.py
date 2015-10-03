from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.conf import settings
from jsonfield import JSONField
from django.db.models.signals import post_save
from django.conf import settings

from tag.models import Tag


class NotifySettings(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="notify_settings")
    interaction = models.BooleanField(_("Interactions regarding my content."), default=True)
    tags_dateos = models.BooleanField(_("Dateos in tags I follow"), default=True)
    tags_reports = models.BooleanField(_("Reports and new Campaigns in tags I follow"), default=True)
    conversations = models.BooleanField(_("Conversations I follow/engage"), default=True)
    site_news = models.BooleanField(_("News by Datea"), default=True)
    
    def __unicode__(self):
        return _('notify settings for')+' '+self.user.username
    
def create_notify_settings(sender, instance=None, **kwargs):
    if instance is None: return
    notify_settings, created = NotifySettings.objects.get_or_create(user=instance)

post_save.connect(create_notify_settings, sender=settings.AUTH_USER_MODEL, dispatch_uid="notifysettings.create")


def save_notify_settings(sender, instance, created, **kwargs):
    if created:
        if instance.site_news:
            settings.EXTERNAL_NEWSLETTER_SUBSCRIBE_FUNC(instance.user, 'subscribe')

post_save.connect(save_notify_settings, sender=NotifySettings, dispatch_uid="notifysettings.save")

        

class Notification(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(_('Type of Notifications'), max_length=30)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="notifications")
    unread = models.BooleanField(_("Unread"), default=True)

    #data = JSONField(verbose_name=_("Data"), blank=True, null=True)
    activity = models.ForeignKey('ActivityLog', verbose_name=_("ActivityLog"), null=True, blank=True)

    # actually used fields:
    # actor: username / id
    # target_user: username / id 
    # verb: verb
    # tags: tags (array of strings) -> sort ones with campaigns first
    # extract: text
    # action_obj_type : (string)
    # action_obj_id
    # target_obj_type : (string)
    # target_obj_id :

    def create_data(self):
        data = {
            "actor": self.activity.actor.username,
            "actor_id": self.activity.actor.pk,
            "actor_img": self.activity.actor.get_small_image(),
            "action_type": self.activity.action_type.model,
            "action_id": self.activity.action_id,
            "extract": self.activity.data.get('extract', ''),
            #"target_object": json.loads(dateo_json),
            "tags": [t.tag for t in self.activity.tags.all().distinct().order_by('campaigns', 'tag')],
            "verb": self.activity.verb,
        }
        if self.activity.target_object:
            data.update({
                "target_type" : self.activity.target_type.model,
                "target_id" : self.activity.target_id,
                "receptor": self.activity.target_user.username,
                "receptor_id" : self.activity.target_user.id,
                "receptor_img": self.activity.target_user.get_small_image()
            })
        return data


    def __unicode__(self):
        return self.type +" notification for " + self.recipient.username


# loosely inspired by https://github.com/justquick/django-activity-stream
class ActivityLog(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(_('Published'), default=True)

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Acting user (actor)"), related_name="acting_user")
    verb = models.CharField(_('Verb'), max_length=50)

    action_object = GenericForeignKey('action_type', 'action_id')
    action_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="action_types")
    action_id = models.PositiveIntegerField(null=True, blank=True)

    action_key = models.CharField(_("Action Key"), max_length=50)

    target_object = GenericForeignKey('target_type', 'target_id')
    target_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="target_types")
    target_id = models.PositiveIntegerField(null=True, blank=True)

    target_key = models.CharField(_("Target Key"), max_length=50)

    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Target user"), related_name="target_user", null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name=_("Tag"), null=True, blank=True)

    data = JSONField(verbose_name=_("Data"), blank=True, null=True)


    def __unicode__(self):
        name = self.actor.username + ' ' + self.verb
        if self.action_type is not None:
            name += " "+str(self.action_type.model)+"."+str(self.action_id)
        if self.target_type is not None:
            name += " on "+str(self.target_type.model)+"."+str(self.target_id)
        return name

    def save(self, *args, **kwargs):

        if self.action_key and not self.action_object:
            try:
                elems = str(self.action_key).split(".")
                self.action_type = ContentType.objects.get(model=elems[0])
                self.action_id = int(elems[1])
            except:
                pass
        elif self.action_object and not self.action_key:
            try:
                self.action_key = self.action_type.model+"."+str(self.action_id)
            except:
                pass

        if self.target_key and not self.target_object:
            try:
                elems = str(self.target_key).split(".")
                self.target_type = ContentType.objects.get(model=elems[0])
                self.target_id = int(elems[1])
            except:
                pass
        elif self.target_object and not self.target_key:
            try:
                self.target_key = self.target_type.model+"."+str(self.target_id)
            except:
                pass

        super(ActivityLog, self).save(*args, **kwargs)


# importing here to avoid circular imports
from notify.search_indexes import ActivityLogIndex
from api.signals import resource_saved
from django.db.models.signals import pre_delete
from django.core.cache import cache

# KEEP HAYSTACK INDEX UP TO DATE IN REALTIME
# -> only happens with calls to the api (tastypie)
def update_search_index(sender, instance, created, **kwargs):
    ActivityLogIndex().update_object(instance)
    cache.delete('actlog.'+str(instance.pk))

def remove_search_index(sender, instance, **kwargs):
    ActivityLogIndex().remove_object(instance)
    cache.delete('actlog.'+str(instance.pk))
    
resource_saved.connect(update_search_index, sender=ActivityLog, dispatch_uid="actlog.saved")
pre_delete.connect(remove_search_index, sender=ActivityLog, dispatch_uid="actlog.delete")

