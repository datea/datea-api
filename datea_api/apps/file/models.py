from django.db import models
from django.utils.translation import ugettext_lazy as _
#from easy_thumbnails.fields import ThumbnailerImageField
#from easy_thumbnails.files import get_thumbnailer
from sorl.thumbnail import default, ImageField, get_thumbnail
from django.conf import settings
from django.db.models.deletion import Collector
from django.db import router
from django.conf import settings

from .fields import ContentTypeRestrictedFileField
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^datea_api\.apps\.file\.fields\.ContentTypeRestrictedFileField"]) 


class File(models.Model):

    user =   models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="files")
    file =   ContentTypeRestrictedFileField(_("File"), upload_to="files")  # 10 MB MAX
    order =  models.IntegerField(blank=True, null=True, default=0)
    
    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.file.url

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _('Files')

    def delete(self, using=None):
        self.clear_nullable_related()
        super(Image, self).delete(using=using)
        
    def clear_nullable_related(self):
        """
        Recursively clears any nullable foreign key fields on related objects.
        Django is hard-wired for cascading deletes, which is very dangerous for
        us. This simulates ON DELETE SET NULL behavior manually.
        """
        for related in self._meta.get_all_related_objects():
            accessor = related.get_accessor_name()
            related_set = getattr(self, accessor)

            if related.field.null:
                related_set.clear()
                print vars(related_set.all())
            else:
                for related_object in related_set.all():
                    related_object.clear_nullable_related()





