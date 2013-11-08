# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django_extensions.db.models import TimeStampedModel


class Datum(TimeStampedModel):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    content = models.TextField(_("Content"))

    position = models.PointField(_('Position'), spatial_index=True)
    address = models.TextField(_('Address'), blank=True, )

    hashtags = models.ManyToManyField('HashTag')

    objects = models.GeoManager()


class HashTag(models.Model):
    value = models.TextField(unique=True)
