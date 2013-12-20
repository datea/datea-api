from django.db import models
from datea_api.apps.account.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from datea.datea_action.models import DateaAction
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.conf import settings

from django.db.models.signals import post_save, pre_delete, m2m_changed

from datea.datea_comment.models import DateaComment
from datea.datea_vote.models import DateaVote
from datea.datea_mapping.models import DateaMapping, DateaMapItem, DateaMapItemResponse
from datea.datea_mapping.signals import map_item_response_created


class DateaNotifySettings(models.Model):
    
    user = models.OneToOneField(User, related_name="notify_settings")
    
    new_content = models.BooleanField(_('new content in my actions'), default=True)
    new_comment = models.BooleanField(_('new comment on my content'), default=True)
    new_vote = models.BooleanField(_('new vote on my content'), default=True)
    new_reply = models.BooleanField(_('new reply on my content'), default=True)
    new_follow = models.BooleanField(_('new follower on my content'), default=True)
     
    notice_from_site = models.BooleanField(_('general news by the site'), default=True)
    notice_from_action = models.BooleanField(_('news from actions I joined'), default=True)
    
    def get_absolute_url(self):
        return '/#/?edit_profile=notify_settings'
    
    def __unicode__(self):
        return _('notify settings for')+' '+self.user.username
    
    
    
def create_notify_settings(sender, instance=None, **kwargs):
    if instance is None: return
    notify_settings, created = DateaNotifySettings.objects.get_or_create(user=instance)

post_save.connect(create_notify_settings, sender=User)
        
     
        
class DateaHistory(models.Model):

    user = models.ForeignKey(User, related_name="sent_notices")
    published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    
    #title = models.TextField(_('Title'), blank=True, null=True)
    extract = models.TextField(_('Extract'), blank=True, null=True)
    
    sender_type = models.CharField(max_length=50)
    receiver_type = models.CharField(max_length=50)
    
    # generic content type relation to the object which receives an action:
    # for example: the content which receives a vote
    # receiver_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="receiver_types")
    # receiver_id = models.PositiveIntegerField(null=True, blank=True)
    # receiver_obj = generic.GenericForeignKey('receiver_type', 'receiver_id')
    
    # generic content type relation to the acting object, for example a "comment"
    acting_type = models.ForeignKey(ContentType, null=True, blank=True, related_name="acting_types")
    acting_id = models.PositiveIntegerField(null=True, blank=True)
    acting_obj = generic.GenericForeignKey('acting_type', 'acting_id')
    
    action = models.ForeignKey(DateaAction, blank=True, null=True, related_name="notices")
    
    # follow_key
    follow_key = models.CharField(max_length=255) # can be an action or a content instance
    history_key =  models.CharField(max_length=255) # a content object
    
    
    def save(self, *args, **kwargs):
        
        self.check_published(save=False)
        super(DateaHistory, self).save(*args, **kwargs)
        
    def delete(self, using=None):
        self.receiver_items.delete()
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
