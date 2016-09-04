from django.db import models
from solo.models import SingletonModel

class ApiConfig(SingletonModel):

    maintainance_mode = models.BooleanField("Maintainance mode", default=False)
    reserved_usernames = models.TextField("Reserved usernames", blank=True, null=True)
    reserved_campaign_names = models.TextField("Reserved campaign names", blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.reserved_usernames:
            self.reserved_usernames = ','.join([u.strip() for u in self.reserved_usernames.split(',')])
        if self.reserved_campaign_names:
            self.reserved_campaign_names = ','.join([c.strip() for c in self.reserved_campaign_names.split(',')])
        super(ApiConfig, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Api Configuration"

    class Meta:
        verbose_name = "Api Configuration"
        verbose_name_plural = verbose_name




######################
#
#   SIGNALS FOR ASYNC ACTIONS WITH CELERY
#
#   need to find a proper place for this,
#   but circular imports and celery's problems
#   with imports prevent this from being more
#   conventional.
#
######################


from django.db.models.signals import post_init, post_save, pre_delete, pre_save
from api.signals import resource_saved
from celery.execute import send_task
from account.models import User
from dateo.models import Dateo, Redateo
from campaign.models import Campaign
from vote.models import Vote
from comment.models import Comment
from flag.models import Flag

def user_saved(sender, instance, created, **kwargs):
    if created:
        global do_user_async_tasks
        from .tasks import do_user_async_tasks
        do_user_async_tasks.delay(instance.pk, notify=True)

post_save.connect(user_saved, sender=User)

####
#  DATEO ASYNC ACTIONS WITH CELERY
#  updating stats, creating activity stream and sending notifications
#  on objects is done using celery
###
def dateo_pre_saved(sender, instance, **kwargs):
    instance._orig_published = instance.published

def dateo_saved(sender, instance, created, **kwargs):
    instance.publish_changed = instance._orig_published != instance.published
    value = 0
    notify = False
    if created and instance.published:
        value = 1
        notify = True
    elif not created and instance.publish_changed and instance.published:
        value = 1
    elif not created and instance.publish_changed and not instance.published:
        value = -1
    if value != 0:
        global do_dateo_async_tasks
        from .tasks import do_dateo_async_tasks
        do_dateo_async_tasks.delay(instance.pk, value, notify)


def dateo_pre_delete(sender, instance, **kwargs):
    if instance.published:
        global do_comment_async_tasks
        from .tasks import do_dateo_async_tasks
        do_dateo_async_tasks(instance, -1, False)

post_init.connect(dateo_pre_saved, sender=Dateo)
resource_saved.connect(dateo_saved, sender=Dateo)
pre_delete.connect(dateo_pre_delete, sender=Dateo)

####
#  REDATEO ASYNC ACTIONS WITH CELERY
###

def redateo_saved(sender, instance, created, **kwargs):
    if created:
        global do_redateo_async_tasks
        from .tasks import do_redateo_async_tasks
        do_redateo_async_tasks.delay(instance, 1, True)

resource_saved.connect(redateo_saved, sender=Redateo)


####
#  VOTE ASYNC ACTIONS WITH CELERY
###
def vote_saved(sender, instance, created, **kwargs):
    if created:
        global do_vote_async_tasks
        from .tasks import do_vote_async_tasks
        do_vote_async_tasks.delay(instance.pk, 1)

def vote_pre_delete(sender, instance, **kwargs):
    global do_vote_async_tasks
    from .tasks import do_vote_async_tasks
    do_vote_async_tasks.delay(instance.pk, -1, False)

post_save.connect(vote_saved, sender=Vote)
pre_delete.connect(vote_pre_delete, sender=Vote)


####
#  COMMENT ASYNC SIGNALS WITH CELERY
###

def comment_pre_saved(sender, instance, **kwargs):
    instance._orig_published = instance.published


def comment_saved(sender, instance, created, **kwargs):
    instance.publish_changed = instance._orig_published != instance.published
    value = 0
    notify = False
    if created and instance.published:
        value = 1
        notify = True
    elif not created and instance.publish_changed and instance.published:
        value = 1
    elif not created and instance.publish_changed and not instance.published:
        value = -1

    if value != 0:
        global do_comment_async_tasks
        from .tasks import do_comment_async_tasks
        do_comment_async_tasks.delay(instance.pk, value, notify)


def comment_pre_delete(sender, instance, **kwargs):
    if instance.published:
        global do_comment_async_tasks
        from .tasks import do_comment_async_tasks
        do_comment_async_tasks(instance.pk, -1, False)

post_init.connect(comment_pre_saved, sender=Comment)
post_save.connect(comment_saved, sender=Comment)
pre_delete.connect(comment_pre_delete, sender=Comment)


######
# CAMPAIGN SAVED
######
def campaign_saved(sender, instance, created, **kwargs):
    if created:
        global do_campaign_async_tasks
        from .tasks import do_campaign_async_tasks
        do_campaign_async_tasks.delay(instance.pk, notify=True)

resource_saved.connect(campaign_saved, sender=Campaign)


#######
#	FLAG SAVED
######

def flag_saved(sender, instance, created, **kwargs):
    if created:
        global do_flag_async_tasks
        from .tasks import do_flag_async_tasks
        do_flag_async_tasks.delay(instance.pk)

post_save.connect(flag_saved, sender=Flag)
