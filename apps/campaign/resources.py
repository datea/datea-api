# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from django_extensions.db.models import AutoSlugField
from django_extensions.db.models import TimeStampedModel


class Campaign(TimeStampedModel):
    user = models.ForeignKey(get_user_model(),
                             verbose_name=_('User'),
                             related_name="campaigns", )
    name = models.TextField(_("Name"), max_length=100)
    slug = AutoSlugField(_('slug'), populate_from='name')
    hashtag = models.
    published = models.BooleanField(_("Published"),
                                    default=True,
                                    help_text=_("If checked, action becomes visible to others"))

    end_date = models.DateTimeField(_('End Date'),
                                    blank=True,
                                    null=True,
                                    help_text=_('Set an end date for your action (optional)'))

    category = models.ForeignKey(Category,
                                 verbose_name=_("Category"),
                                 blank=True,
                                 null=True,
                                 related_name="campaigns",
                                 help_text=_("Choose a category for this action"))

    # image = models.ForeignKey(Image,
    #                           verbose_name=_('Image'),
    #                           blank=True,
    #                           null=True,
    #                           related_name="campaigns")

    # statistics For Campaing Resource
    @property
    def item_count(self):
        """
        How many datums the initiative have
        """
        models.PositiveIntegerField(_("Item count"), default=0)

    @property
    def user_count(self):
        """
        How many users are reported to the campaign
        """
        models.PositiveIntegerField(_("Participant count"), default=0)

    @property
    def comment_count(self):
        """
        How many comments are there
        """
        comment_count = models.PositiveIntegerField(_('Comment count'), default=0)

    @property
    def follow_count(self):
        """
        How many users follow the campain
        """
        models.PositiveIntegerField(_('Follower count'), default=0)


class FeaturedCampaigns(models.Model):
    """The Group of Highlighted Campaings for the frontpage.
    """
    campaign = models.ForeignKey(Campaign
                                 verbose_name=_('Image'), )

class Category(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    slug = AutoSlugField(_('slug'), populate_from='name')
    description = models.TextField(_('Description (optional)'),
                                   max_length=500,
                                   blank=True, )
    active = models.BooleanField(_('is active'),
                                 default=True)
    color = models.CharField(max_length=7,
                             default='#CCCCCC')
