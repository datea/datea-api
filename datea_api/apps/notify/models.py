from django.db import models
from account.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.conf import settings
from jsonfield import JSONField
from django.db.models.signals import post_save

from tag.models import Tag


class NotifySettings(models.Model):
    
    user = models.OneToOneField(User, related_name="notify_settings")
    interaction = models.BooleanField(_("Interactions regarding my content."), default=True)
    tags_dateos = models.BooleanField(_("Dateos in tags I follow"), default=False)
    tags_reports = models.BooleanField(_("Reports in tags I follow"), default=True)
    conversations = models.BooleanField(_("Conversations I follow/engage"), default=True)
    site_news = models.BooleanField(_("News by Datea"), default=True)
    
    def __unicode__(self):
        return _('notify settings for')+' '+self.user.username
    
def create_notify_settings(sender, instance=None, **kwargs):
    if instance is None: return
    notify_settings, created = NotifySettings.objects.get_or_create(user=instance)

post_save.connect(create_notify_settings, sender=User)
        

class Notification(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(_('Type of Notifications'), max_length=30)
    recipient = models.ForeignKey(User, verbose_name=_("User"))
    unread = models.BooleanField(_("Unread"), default=True)

    data = JSONField(verbose_name=_("Data"), blank=True, null=True)
    activity = models.ForeignKey('ActivityLog', verbose_name=_("ActivityLog"), null=True, blank=True)

    def __unicode__(self):
        return self.type +" notification for " + self.recipient.username



# loosely inspired in https://github.com/justquick/django-activity-stream
class ActivityLog(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(_('Published'), default=True)

    actor = models.ForeignKey(User, verbose_name=_("Acting user (actor)"), related_name="acting_user")
    verb = models.CharField(_('Verb'), max_length=50)

    action_object = generic.GenericForeignKey('action_type', 'action_id')
    action_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="action_types")
    action_id = models.PositiveIntegerField(null=True, blank=True)

    action_key = models.CharField(_("Action Key"), max_length=50)

    target_object = generic.GenericForeignKey('target_type', 'target_id')
    target_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="target_types")
    target_id = models.PositiveIntegerField(null=True, blank=True)

    target_key = models.CharField(_("Target Key"), max_length=50)

    target_user = models.ForeignKey(User, verbose_name=_("Target user"), related_name="target_user", null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name=_("Tag"), null=True, blank=True)

    data = JSONField(verbose_name=_("Data"), blank=True, null=True)


    def __unicode__(self):
        name = self.actor.username + ' ' + self.verb
        if self.action_type is not None:
            name += " "+self.action_type.model+"."+str(self.action_id)
        if self.target_type is not None:
            name += " on "+self.target_type.model+"."+str(self.target_id)

    def save(self, *args, **kwargs):

        if self.action_key is not None and self.action_object is None:
            try:
                elems = str(self.action_key).split(".")
                self.action_type = ContentType.objects.get(model=elems[0])
                self.action_id = int(elems[1])
            except:
                pass
        elif self.action_object is not None and self.action_key is None:
            try:
                self.action_key = self.action_type.model+"."+str(self.action_id)
            except:
                pass

        if self.target_key is not None and self.target_object is None:
            try:
                elems = str(self.target_key).split(".")
                self.target_type = ContentType.objects.get(model=elems[0])
                self.target_id = int(elems[1])
            except:
                pass
        elif self.target_object is not None and self.target_key is None:
            try:
                self.target_key = self.target_type.model+"."+str(self.target_id)
            except:
                pass

        super(Activity, self).save(*args, **kwargs)



'''        
class History(models.Model):

    follow_key = models.CharField(max_length=50) # key to identify who should see this
    object_key = models.CharField(max_length=50) # key to identify the sending object rapidly

    acting_user = models.ForeignKey(User, null=True, blank=True)
    affected_user = models.ForeignKey(User, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    
    receiver_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="receiver_types")
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver_obj = generic.GenericForeignKey('receiver_type', 'receiver_id')
    
    # generic content type relation to the acting object, for example a "comment"
    acting_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="acting_types")
    acting_id = models.PositiveIntegerField(null=True, blank=True)
    acting_obj = generic.GenericForeignKey('acting_type', 'acting_id')

    title_verb = model.CharField(_('verb'), max_length=255, null=True, blank=True)

    
    def save(self, *args, **kwargs):  
        self.check_published(save=False)
        super(DateaHistory, self).save(*args, **kwargs)
        
    def delete(self, using=None):
        super(DateaHistory, self).delete(using=using)
        
    def generate_extract(self, object_type, object_instance):
        context = {'instance': object_instance}
        self.extract = render_to_string('history/%s/extract.html' % object_type, context)
        
        
    def check_published(self, save=True):
        # TODO -> optimization!
        recv_pub = False
        for recv_item in self.receiver_items.all():
            if recv_item.published:
                recv_pub = True
                break
            
        if self.published != recv_pub:
            self.published = recv_pub
                
        elif self.acting_obj:
            if hasattr(self.acting_obj, 'published') and self.acting_obj.published != self.published:
                self.published = self.acting_obj.published
                
            elif hasattr(self.acting_obj, 'active') and self.acting_obj.active != self.published:
                self.published = self.acting_obj.active
                
        if save: 
            self.save()
        
        
    # context names at the moment: content, comment, vote
    def send_mail_to_receivers(self, context_name):
        # at the moment, only sending emails to owners of receiver objects
        # not sending when acting upon own content
        for instance in self.receiver_items.all():
            owner = instance.user
            #notify_settings = owner.notify_settings
            notify_settings, created = DateaNotifySettings.objects.get_or_create(user=owner)
        
            if (getattr(owner.notify_settings, 'new_'+context_name)
                and owner != self.user 
                and owner.email):
                
                current_site = Site.objects.get_current()
                context = {
                        'user': owner,
                        'receiver_obj': instance.content_obj,
                        'acting_obj': self.acting_obj,
                        'site': current_site,
                        'settings_url': owner.notify_settings.get_absolute_url()       
                }
                
                mail_subject = render_to_string(
                        'mail/%s/%s/mail_subject_owner.txt' % (instance.content_type.model, context_name), 
                        context).replace("\n",'')
                
                mail_body = render_to_string(
                        'mail/%s/%s/mail_body_owner.txt' % (instance.content_type.model, context_name), 
                        context)
                
                email = EmailMessage(
                        mail_subject, 
                        mail_body, 
                        current_site.name+' <'+settings.DEFAULT_FROM_EMAIL+'>',
                        [owner.email]
                        )
                email.send()
    
    
    def send_mail_to_action_owner(self, context_name):
        if self.action:
            owner = self.action.user
            instance = self.receiver_items.all()[0]
            
            #notify_settings = owner.notify_settings
            notify_settings, created = DateaNotifySettings.objects.get_or_create(user=owner)
            
            if (getattr(owner.notify_settings, 'new_'+context_name)
                and owner != self.user 
                and owner.email):
                
                current_site = Site.objects.get_current()
                context = {
                        'user': owner,
                        'receiver_obj': instance.content_obj,
                        'acting_obj': self.acting_obj,
                        'site': current_site,
                        'settings_url': owner.notify_settings.get_absolute_url()       
                }
                
                mail_subject = render_to_string(
                        'mail/%s/%s/mail_subject_generic.txt' % (instance.content_type.model, context_name), 
                        context).replace("\n",'')
                
                mail_body = render_to_string(
                        'mail/%s/%s/mail_body_generic.txt' % (instance.content_type.model, context_name), 
                        context)
                
                email = EmailMessage(
                        mail_subject, 
                        mail_body, 
                        current_site.name+' <'+settings.DEFAULT_FROM_EMAIL+'>',
                        [owner.email]
                        )
                email.send()
    
            
class DateaHistoryReceiver(models.Model):
    
    user = models.ForeignKey(User)
    
    name = models.CharField(_('name'), max_length=255)
    url = models.URLField(_('url'), verify_exists=False)
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="receiver_types")
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_obj = generic.GenericForeignKey('content_type', 'object_id')
    
    #object_type = models.CharField(max_length=255)
    #object_id = models.PositiveIntegerField()
    
    published = models.BooleanField(_('published'), default=True)
    
    history_item = models.ForeignKey('DateaHistory', verbose_name=_('history item'), related_name="receiver_items")
    
    
    def check_published(self, save=False):
        if self.published != self.content_obj.published:
            self.published = self.content_obj.published
            if save:
                self.save()
        return self.published
    
            
    def save(self, *args, **kwargs):
        self.check_published(save=False)
        super(DateaHistoryReceiver, self).save(*args, **kwargs)
    
       
    def __unicode__(self):
        return self.name+' <'+self.url+'>'
     
   
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONNECT HISTORY NOTICES SIGNALS FOR ALL DATEA APPS!         
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from signal_handlers import comment, follow, mapping, vote, action
    
comment.connect()
follow.connect()
mapping.connect()
vote.connect()
action.connect()
'''