from django.db import models
from sorl.thumbnail import default, ImageField, get_thumbnail
from django.conf import settings
from django.db.models.deletion import Collector
from django.db import router

from file.fields import ContentTypeRestrictedFileField


class File(models.Model):

    user  =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", related_name="files")
    title =  models.CharField('Title', max_length=128, blank=True, null=True)
    file  =  ContentTypeRestrictedFileField("File", upload_to="files")  # 10 MB MAX
    order =  models.IntegerField(blank=True, null=True, default=0)
    client_domain = models.CharField('CLient Domain', max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.file.url

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.file.url.split('/')[-1]
        super(File, self).save(*args, **kwargs)
