# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class PublishedModelManager(models.Model):
    """
    TODO: Evaluate if it is this is really needed.
    """
    def published(self):
        return self.get_query_set().filter(status=True)

    def unpublished(self):
        return self.get_query_set().filter(published=False)


class PublishedModel(models.Model):
    published = models.BooleanField(_("Published"),
                                    default=True,
                                    help_text=_("If checked, action becomes visible to others"))

    objects = PublishedModelManager()

    class Meta:
        abstract = True
