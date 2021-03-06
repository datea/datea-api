from __future__ import absolute_import
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from types import IntType
#import bleach -> bleach is not working. Wait for new version.
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext
import json

from account.models import User
from campaign.models import Campaign
from campaign.resources import CampaignResource
from notify.models import ActivityLog, Notification
from follow.models import Follow
from comment.models import Comment
from comment.resources import CommentResource
from dateo.models import Dateo, Redateo
from dateo.resources import DateoResource
from vote.models import Vote
import vote.resources
from flag.models import Flag

from notify.utils import send_mails, send_admin_mail
from account.utils import get_client_data

from api.signals import resource_saved

from django.db import IntegrityError, transaction
from django.conf import settings

################################### USER ASYNC TASKS  #######################################
@shared_task
def do_user_async_tasks(user_obj, notify=False):

    if type(user_obj) == IntType:
        with transaction.atomic():
            user_obj = User.objects.get(pk=user_obj)

    if notify:
        email_data = {
                'user': user_obj
        }
        send_admin_mail('user', email_data)

################################### DATEO ASYNC TASKS #######################################

@shared_task
def do_dateo_async_tasks(dateo_obj, stat_value, notify=False):

    if type(dateo_obj) == IntType:
        with transaction.atomic():
            dateo_obj = Dateo.objects.get(pk=dateo_obj)

    if notify and stat_value > 0:
        actlog = create_dateo_activity_log(dateo_obj)
        create_dateo_notifications(actlog)


@shared_task
def create_dateo_activity_log(dateo):

    actlog = ActivityLog()
    actlog.actor = dateo.user
    actlog.verb = 'dateo'
    actlog.action_object = dateo

    #tr = Truncator(bleach.clean(dateo.content, strip=True))
    tr = Truncator(strip_tags(dateo.content))
    extract = tr.chars(140)
    actlog.data = {'extract': extract}
    actlog.save()

    actlog.tags.add(*dateo.tags.all())

    resource_saved.send(sender=ActivityLog, instance=actlog, created=True)

    return actlog

@shared_task
def create_dateo_notifications(actlog):

    email_users = set()
    notify_users = set()

    # 1. Seguidores de tags
    follow_keys = ['tag.'+str(tag.pk) for tag in actlog.action_object.tags.all()]
    follows = Follow.objects.filter(follow_key__in=follow_keys)
    for f in follows:
        notify_users.add(f.user)
        if f.user.notify_settings.tags_dateos:
            email_users.add(f.user)

    # 2. Duenhos de iniciativas
    if hasattr(actlog.action_object, 'tags'):
        for tag in actlog.action_object.tags.all():
            for c in tag.campaigns.all():
                notify_users.add(c.user)
                if c.user.notify_settings.interaction:
                    email_users.add(c.user)

    for user in notify_users:
        n = Notification(type="dateo", recipient=user, activity=actlog)
        n.save()

    # email using target_object client_domain (for now)
    client_data = get_client_data(actlog.action_object.client_domain)
    if not client_data['send_notification_mail']:
        return
    dateo_url = client_data['dateo_url'].format(username=actlog.action_object.user.username,
                            user_id=actlog.action_object.user.pk, obj_id=actlog.action_object.pk)

    email_data = {
            "actor": actlog.actor.username,
            "extract": actlog.data.get('extract', ''),
            "content": actlog.action_object.content,
            "url": dateo_url,
            "created": actlog.created,
            "site": client_data
    }

    if hasattr(actlog.action_object, 'tags'):
        email_data["tags"] = [tag.tag for tag in actlog.action_object.tags.all()]

    if len(email_users) > 0 :
        send_mails(email_users, "dateo", email_data)

    send_admin_mail("dateo", email_data)


############################################## REDATEO ASYNC TASKS ##########################################

@shared_task
def do_redateo_async_tasks(redateo_obj, stat_value, notify=False):

    if type(redateo_obj) == IntType:
        with transaction.atomic():
            redateo_obj = Redateo.objects.get(pk=redateo_obj)

    if notify and stat_value > 0:
        actlog = create_redateo_activity_log(redateo_obj)
        create_redateo_notifications(actlog)


@shared_task
def create_redateo_activity_log(redateo):

    actlog = ActivityLog()
    actlog.actor = redateo.user
    actlog.verb = 'redateo'
    actlog.action_object = redateo
    actlog.target_object = redateo.dateo

    #tr = Truncator(bleach.clean(redateo.dateo.content, strip=True))
    tr = Truncator(strip_tags(redateo.dateo.content))
    extract = tr.chars(100)
    actlog.data = {'extract': extract}
    actlog.target_user = redateo.dateo.user

    actlog.save()

    actlog.tags.add(*redateo.dateo.tags.all())

    resource_saved.send(sender=ActivityLog, instance=actlog, created=True)

    return actlog


@shared_task
def create_redateo_notifications(actlog):

    # 1. Usuario afectado
    notify_users = set([actlog.target_user])
    email_users = set()

    if actlog.target_user.notify_settings.interaction:
        email_users.add(actlog.target_user)

    # 3. Seguidores de hilo
    follows = Follow.objects.filter(follow_key=actlog.target_key)
    for f in follows:
        notify_users.add(f.user)
        if f.user.notify_settings.conversations:
            email_users.add(f.user)

    # 4. Duenhos de iniciativas
    for tag in actlog.target_object.tags.all():
        for c in tag.campaigns.all():
            notify_users.add(c.user)
            if c.user.notify_settings.interaction:
                email_users.add(c.user)

    for user in notify_users:
        n = Notification(type="redateo", recipient=user, activity=actlog)
        n.save()

    # email using target_object client_domain
    client_data = get_client_data(actlog.target_object.client_domain)
    if not client_data['send_notification_mail']:
        return
    dateo_url = client_data['dateo_url'].format(username=actlog.target_object.user.username,
                            user_id=actlog.target_object.user.pk, obj_id=actlog.target_id)

    email_data = {
            "actor": actlog.actor.username,
            "target_user": actlog.target_user.username,
            "target_object_name": ugettext(actlog.target_type.model),
            "dateo": actlog.target_object,
            "extract": actlog.data['extract'],
            "url": dateo_url,
            "created": actlog.created,
            "site": client_data,
    }
    if hasattr(actlog.target_object, 'tags'):
        email_data["tags"] = [tag.tag for tag in actlog.target_object.tags.all()]

    if len(email_users) > 0:
        send_mails(email_users, "redateo", email_data)

    send_admin_mail("redateo", email_data)




############################################## COMMENT ASYNC TASKS ##########################################

@shared_task
def do_comment_async_tasks(comment_obj, stat_value, notify=False):

    if type(comment_obj) == IntType:
        with transaction.atomic():
            comment_obj = Comment.objects.get(pk=comment_obj)

    if notify and stat_value > 0:
        actlog = create_comment_activity_log(comment_obj)
        create_comment_notifications(actlog)


@shared_task
def create_comment_activity_log(comment):

    actlog = ActivityLog()
    actlog.actor = comment.user
    actlog.verb = 'commented'
    actlog.action_object = comment
    actlog.target_object = comment.content_object

    #tr = Truncator(bleach.clean(comment.comment, strip=True))
    tr = Truncator(strip_tags(comment.comment))
    extract = tr.chars(100)
    actlog.data = {'extract': extract}

    if hasattr(comment.content_object, "user"):
        actlog.target_user = comment.content_object.user

    actlog.save()

    if hasattr(comment.content_object, "tags"):
        actlog.tags.add(*comment.content_object.tags.all())

    resource_saved.send(sender=ActivityLog, instance=actlog, created=True)

    return actlog

@shared_task
def create_comment_notifications(actlog):

    # 1. Usuario afectado
    notify_users = set()
    email_users = set()

    if actlog.target_user.notify_settings.interaction and actlog.actor != actlog.target_user:
        email_users.add(actlog.target_user)

    # 3. Seguidores de hilo
    follows = Follow.objects.filter(follow_key=actlog.target_key)
    for f in follows:
        if f.user != actlog.actor:
            notify_users.add(f.user)
            if f.user.notify_settings.conversations:
                email_users.add(f.user)

    # 4. Duenhos de iniciativas
    if hasattr(actlog.target_object, 'tags'):
        for tag in actlog.target_object.tags.all():
            for c in tag.campaigns.all():
                if c.user != actlog.actor:
                    notify_users.add(c.user)
                    if c.user.notify_settings.interaction:
                        email_users.add(c.user)

    for user in notify_users:
        n = Notification(type="comment", recipient=user, activity=actlog)
        n.save()

    # email using target_object client_domain (for now)
    client_data = get_client_data(actlog.target_object.client_domain)
    if not client_data['send_notification_mail']:
        return

    comment_url = client_data['comment_url'].format(username=actlog.target_object.user.username,
                            user_id=actlog.target_object.user.pk, obj_id=actlog.target_id,
                            obj_type= actlog.target_type.model, comment_id=actlog.action_id)

    email_data = {
            "actor": actlog.actor.username,
            "target_user": actlog.target_user.username,
            "target_object_name": ugettext(actlog.target_type.model),
            "comment": actlog.action_object.comment,
            "extract": actlog.data['extract'],
            "url": comment_url,
            "created": actlog.created,
            "site": client_data,
    }
    if hasattr(actlog.target_object, 'main_tag'):
        email_data['tags'] = [actlog.target_object.main_tag.tag]
    if hasattr(actlog.target_object, 'tags'):
        email_data['tags'] = map(lambda t: t.tag, actlog.target_object.tags.all())

    if len(email_users) > 0:
        send_mails(email_users, "comment", email_data)

    send_admin_mail("comment", email_data)


############################################## CAMPAIGN ASYNC TASKS ######################################
@shared_task
def do_campaign_async_tasks(campaign_obj, notify=False):

    if type(campaign_obj) == IntType:
        # doing strange stuff because of circular imports and celery
        with transaction.atomic():
            campaign_obj = Campaign.objects.get(pk=campaign_obj)

    if notify:
        actlog = create_campaign_activity_log(campaign_obj)
        create_campaign_notifications(actlog)


@shared_task
def create_campaign_activity_log(campaign):

    actlog = ActivityLog()
    actlog.actor = campaign.user
    actlog.verb = 'campaign'
    actlog.action_object = campaign
    actlog.action_key = 'tag.'+str(campaign.main_tag.pk)

    actlog.data = {'extract': campaign.short_description}
    actlog.save()

    actlog.tags.add(campaign.main_tag)

    resource_saved.send(sender=ActivityLog, instance=actlog, created=True)

    return actlog


@shared_task
def create_campaign_notifications(actlog):

    notify_users = set()
    email_users  = set()

    follows = Follow.objects.filter(follow_key=actlog.action_key)
    for f in follows:
        notify_users.add(f.user)
        if f.user.notify_settings.tags_reports:
            email_users.add(f.user)

    for user in notify_users:
        n = Notification(type="campaign", recipient=user, activity=actlog)
        n.save()

    # email using target_object client_domain (for now)
    client_data = get_client_data(actlog.action_object.client_domain)
    if not client_data['send_notification_mail']:
        return
    campaign_url = client_data['campaign_url'].format(username=actlog.action_object.user.username,
                            user_id=actlog.action_object.user.pk, obj_id=actlog.action_id, tag_name=actlog.action_object.main_tag.tag)

    email_data = {
            "actor": actlog.actor.username,
            "action_object_name": ugettext(actlog.action_type.model),
            "title": actlog.action_object.name,
            "extract": actlog.data.get('extract', ''),
            "url": campaign_url,
            "created": actlog.created,
            "site": client_data,
            "tag" : actlog.action_object.main_tag.tag
    }

    if len(email_users) > 0:
        send_mails(email_users, "campaign", email_data)

    send_admin_mail("campaign", email_data)




############################################## VOTE ASYNC TASKS ##########################################

@shared_task
def do_vote_async_tasks(vote_obj, stat_value, notify=False):

    if type(vote_obj) == IntType:
        # doing strange stuff because of circular imports and celery
        with transaction.atomic():
            vote_obj = Vote.objects.get(pk=vote_obj)

    if notify and stat_value > 0:
        actlog = create_vote_activity_log(vote_obj)
        create_vote_notifications(actlog)


@shared_task
def create_vote_activity_log(vote):

    actlog = ActivityLog()
    actlog.actor = vote.user
    actlog.verb = 'vote'
    actlog.action_object = vote
    actlog.target_object = vote.content_object

    if hasattr(vote.content_object, 'content'):
        #tr = Truncator(bleach.clean(vote.content_object.content, strip=True))
        tr = Truncator(strip_tags(vote.content_object.content))
        extract = tr.chars(140)
        actlog.data = {'extract': extract}

    if hasattr(vote.content_object, "user"):
        actlog.target_user = comment.content_object.user

    actlog.save()

    if hasattr(vote.content_object, "tags"):
        actlog.tags.add(*vote.content_object.tags.all())

    resource_saved.send(sender=ActivityLog, instance=actlog, created=True)

    return actlog

@shared_task
def create_vote_notifications(actlog):

    # 1. Usuario afectado
    notify_users = set([actlog.target_user])
    email_users = set()

    if actlog.target_user.notify_settings.interaction:
        email_users.add(actlog.target_user)

    # 2. Seguidores de hilo
    #follows = Follow.objects.filter(follow_key=actlog.target_key)
    #for f in follows:
    #	notify_users.append(f.user)
    #	if f.user.notify_settings.conversations:
    #		email_users.append(f.user)

    # 3. Duenhos de iniciativas
    if hasattr(actlog.target_object, 'tags'):
        for tag in actlog.target_object.tags.all():
            for c in tag.campaigns.all():
                notify_users.add(c.user)
                if c.user.notify_settings.interaction:
                    email_users.add(c.user)

    for user in notify_users:
        n = Notification(type="vote", recipient=user, activity=actlog)
        n.save()

    # email using target_object client_domain (for now)
    client_data = get_client_data(actlog.target_object.client_domain)
    if not client_data['send_notification_mail']:
        return
    dateo_url = client_data['dateo_url'].format(username=actlog.target_object.user.username,
                            user_id=actlog.target_object.user.pk, obj_id=actlog.target_object.pk)

    email_data = {
            "actor": actlog.actor.username,
            "target_user": actlog.target_user.username,
            "target_object_name": ugettext(actlog.target_type.model),
            "extract": actlog.data.get('extract', ''),
            "url": dateo_url,
            "created": actlog.created,
            "site": client_data
    }

    if hasattr(actlog.target_object, 'tags'):
        email_data["tags"] = [tag.tag for tag in actlog.target_object.tags.all()]
    if hasattr(actlog.target_object, 'content'):
        email_data["content"] = actlog.target_object.content

    if len(email_users) > 0:
        send_mails(email_users, "vote", email_data)

    send_admin_mail("vote", email_data)


############################################## FLAG ASYNC TASKS ##########################################

@shared_task
def do_flag_async_tasks(flag_obj_id):

    # doing strange stuff because of circular imports and celery
    with transaction.atomic():
        flag_obj = Flag.objects.get(pk=flag_obj_id)

    client_data = get_client_data(flag_obj.client_domain)
    url = ''

    if flag_obj.content_type.model == 'dateo':
        url = client_data['dateo_url'].format(username=flag_obj.content_object.user.username,
                        user_id=flag_obj.content_object.user.pk, obj_id=flag_obj.content_object.pk)

    elif flag_obj.content_type.model == 'comment':
        url = client_data['comment_url'].format(username=flag_obj.content_object.user.username,
                        user_id=flag_obj.content_object.user.pk, obj_id=flag_obj.content_object.content_object.pk,
                        comment_id=flag_obj.object_id, obj_type=flag_obj.content_object.content_type.model)

    elif flag_obj.content_type.model == 'campaign':
        url = client_data['campaign_url'].format(username=flag_obj.content_object.user.username,
                        user_id=flag_obj.content_object.user.pk, obj_id=flag_obj.content_object.pk, slug=flag_obj.content_object.slug)

    email_data = {
            "actor": flag_obj.user.username,
            "app_label": flag_obj.content_type.app_label,
            "target_user": flag_obj.content_object.user.username,
            "target_object": flag_obj.content_object,
            "model": flag_obj.content_type.model,
            "object_id": flag_obj.object_id,
            "comment": flag_obj.comment,
            "url": url,
            "site": client_data
    }

    send_admin_mail("flag", email_data)
