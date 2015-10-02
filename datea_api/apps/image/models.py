from django.db import models
from django.utils.translation import ugettext_lazy as _
#from easy_thumbnails.fields import ThumbnailerImageField
#from easy_thumbnails.files import get_thumbnailer
from sorl.thumbnail import default, ImageField, get_thumbnail
from django.conf import settings
from django.db.models.deletion import Collector
from django.db import router
from django.conf import settings
from django_resized import ResizedImageField


class Image(models.Model):
 
    image =  ResizedImageField(size=[2048, 2048], upload_to="images")  
    user =   models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="images")
    order =  models.IntegerField(blank=True, null=True, default=0)
    width =  models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)

    client_domain = models.CharField(_('CLient Domain'), max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.image.url


    def get_thumb(self, preset='image_thumb'):
        Preset = settings.THUMBNAIL_PRESETS[preset]
        #preserve format
        ext = self.image.url.split('.')[-1].upper()
        if ext not in ['PNG', 'JPG'] or ext == 'JPG':
            ext = 'JPEG'
        options = {'format': ext }
        if 'options' in Preset:
            options.update(Preset['options'])
        return get_thumbnail(self.image, Preset['size'], **options).url


    def save(self, *args, **kwargs):
        if not self.image._file:
            image = default.engine.get_image(self.image)
            (self.width, self.height) = default.engine.get_image_size(image)
        super(Image, self).save(*args, **kwargs)
        

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _('Images')


