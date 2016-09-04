from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings


class Flag(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='User', related_name="flags")
    created = models.DateTimeField('created', auto_now_add=True)

    # generic content type relation to flagged object
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField(null=True, blank=True)

    comment = models.TextField("Comentario", blank=True, null=True)

    client_domain = models.CharField('CLient Domain', max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.user.username + ": " + self.content_type.model + "." + str(self.object_id)

    class Meta:
        verbose_name = 'Flag'
        verbose_name_plural = 'Flags'
