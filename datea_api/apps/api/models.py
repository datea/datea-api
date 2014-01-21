
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


####
#  DATEO ASYNC ACTIONS WITH CELERY
#  better implemented with signals, if you'd like to turn this off.
#  updating stats, creating activity stream and sending notifications 
#  on objects is done using celery
###
from django.db.models.signals import post_init, post_save, pre_delete
from .signals import resource_saved
from celery.execute import send_task
from datea_api.apps.dateo.models import Dateo
from datea_api.apps.vote.models import Vote
from datea_api.apps.comment.models import Comment


def dateo_pre_saved(sender, instance, **kwargs):
	instance.__orig_published = instance.published

def dateo_saved(sender, instance, created, **kwargs):
	instance.publish_changed = instance.__orig_published != instance.published
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
    instance.__orig_published = instance.published


def comment_saved(sender, instance, created, **kwargs):
    instance.publish_changed = instance.__orig_published != instance.published
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


