from django.db import models
from django.utils.translation import ugettext_lazy as _
#from easy_thumbnails.fields import ThumbnailerImageField
#from easy_thumbnails.files import get_thumbnailer
from sorl.thumbnail import default, ImageField, get_thumbnail
from django.conf import settings
from django.db.models.deletion import Collector
from django.db import router

from .fields import ContentTypeRestrictedFileField
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^datea_api\.apps\.file\.fields\.ContentTypeRestrictedFileField"]) 


class File(models.Model):

    user  =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="files")
    title =  models.CharField(_('Title'), max_length=128, blank=True, null=True)
    file  =  ContentTypeRestrictedFileField(_("File"), upload_to="files")  # 10 MB MAX
    order =  models.IntegerField(blank=True, null=True, default=0)
    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.file.url

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _('Files')

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.file.url.split('/')[-1]
        super(File, self).save(*args, **kwargs)






