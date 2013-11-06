# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel

from utils.models import PublishedModel
from datum.models import HashTag


class Campaign(PublishedModel, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_('User'),
                             related_name="campaigns")

    name = models.CharField(_("Name"), max_length=100)
    slug = AutoSlugField(_('slug'), populate_from='name')

    slogan = models.CharField(_("Short description / Slogan"),
                              blank=True,
                              max_length=140,
                              help_text=_("A short description or slogan (max. 140 characters)."))

    hashtag = models.OneToOne(HashTag,
                              verbose_name=_("Hashtag"),
                              help_text=_("A twitter hashtag for your action"))
    category = models.ForeignKey(Category,
                                 verbose_name=_("Category"),
                                 related_name="campaign",
                                 help_text=_("Choose a category for this action"))

    end_date = models.DateTimeField(_('End Date'),
                                    null=True,
                                    blank=True,
                                    help_text=_('Set an end date for your action (optional)'))

    # image = models.ForeignKey(DateaImage,
    #                           verbose_name=_('Image'),
    #                           blank=True,
    #                           null=True,
    #                           related_name="campaigns")
