# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel


class Datum(TimeStampedModel):
    # Missing User
    content = models.TextField(_("Content"))

    position = models.PointField(_('Position'), spatial_index=True)
    address = models.TextField(_('Address'),blank=True, )

    objects = models.GeoManager()
