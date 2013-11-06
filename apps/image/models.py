# -*- coding: utf-8 -*-
from django.db import models
from django.db.signals import pre_save
from django.contrib.auth import get_user_model


class DateaImage(models.Model):
    image = ImageField(upload_to="images")
    user = models.ForeignKey(get_user_model(),
                             verbose_name=_("User"))
    order = models.IntegerField(blank=True, null=True, default=0)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    def save(self, *args, **kwargs):

        if not self.image._file:
            image = default.engine.get_image(self.image)
            (self.width, self.height) = default.engine.get_image_size(image)
        super(DateaImage, self).save(*args, **kwargs)
