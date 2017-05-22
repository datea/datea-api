from django.contrib.gis.db import models
from django.conf import settings
from django.utils.html import strip_tags

from tag.models import Tag
from campaign.models import Campaign
from category.models import Category
from image.models import Image
from file.models import File
from link.models import Link
from follow.models import Follow
import urllib2, json
from django.core.cache import cache
from django.utils.html import strip_tags


class Dateo(models.Model):

    user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", related_name="dateos", on_delete=models.DO_NOTHING)

    # timestamps
    created = models.DateTimeField('created', auto_now_add=True)
    modified = models.DateTimeField('modified', auto_now=True)

    # status, published
    published = models.BooleanField("published", default=True)
    status_choices = (
        ('new','new'),
        ('reviewed', 'reviewed'),
        ('solved', 'solved')
    )
    status = models.CharField("status", max_length=15, choices=status_choices, default="new")

    # content
    content = models.TextField("Content")
    images = models.ManyToManyField(Image, verbose_name='Images', blank=True, related_name="dateo")
    files = models.ManyToManyField(File, verbose_name='Files', blank=True, related_name="dateo")
    link  = models.ForeignKey(Link, verbose_name='Link', null=True, blank=True, related_name="dateos", on_delete=models.SET_NULL)

    # location
    position = models.PointField('Position', blank=True, null=True, spatial_index=False)
    address = models.CharField('Address', max_length=255, blank=True, null=True)

    # optional relationship to campaign
    campaign = models.ForeignKey(Campaign, related_name="dateos", blank=True, null=True, on_delete=models.SET_NULL)

    # category
    category = models.ForeignKey(Category, verbose_name="Category", null=True, blank=True, default=None, related_name="dateos", on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, verbose_name="Tags", related_name="dateos");

    # stats
    vote_count = models.IntegerField(default=0, blank=True, null=True)
    comment_count = models.IntegerField(default=0,blank=True, null=True)
    #follow_count = models.IntegerField(default=0, blank=True, null=True)
    redateo_count = models.IntegerField(default=0, blank=True, null=True)

    date = models.DateTimeField('Date', blank=True, null=True)
    client_domain = models.CharField('CLient Domain', max_length=100, blank=True, null=True)

    # Administrative levels
    country = models.CharField('Country', max_length=100, blank=True, null=True)
    admin_level1 = models.CharField('Administrative level 1', max_length=127, blank=True, null=True)
    admin_level2 = models.CharField('Administrative level 2', max_length=127, blank=True, null=True)
    admin_level3 = models.CharField('Administrative level 3', max_length=127, blank=True, null=True)

    # Object Manager from geodjango
    objects = models.GeoManager()

    def __unicode__(self):
        return self.user.username + ': ' + strip_tags(self.content)[:100]

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = self.created
        self.get_administrative_levels()
        self.content = strip_tags(self.content)
        super(Dateo, self).save(*args, **kwargs)

    def has_images(self):
        return self.images.count() > 0

    def has_files(self):
        return self.files.count() > 0

    def get_absolute_url(self):
        return '/'+self.user.username+'/dateos/'+str(self.pk)

    def get_next_id_by_user(self):
        qs = self.__class__._default_manager.using(self._state.db).filter(created__gt=self.created, user=self.user).order_by('created')
        try:
            return qs[0].id
        except:
            try:
                qs = self.__class__._default_manager.using(self._state.db).filter(user=self.user).exclude(pk=self.pk).order_by('created')
                return qs[0].id
            except:
                return None

    def get_previous_id_by_user(self):
        qs = self.__class__._default_manager.using(self._state.db).filter(created__lt=self.created, user=self.user).order_by('-created')
        try:
            return qs[0].id
        except:
            try:
                qs =self.__class__._default_manager.using(self._state.db).filter(user=self.user).exclude(pk=self.pk).order_by('-created')
                return qs[0].id
            except:
                return None


    def get_administrative_levels(self, save=False):
        if self.position:
            xy = str(self.position.get_x())+','+str(self.position.get_y())
            url = 'http://global.mapit.mysociety.org/point/'+str(self.position.srid)+'/'+xy
            f = urllib2.urlopen(url)
            data = json.load(f)
            extract = {}
            for key,item in data.iteritems():
                extract[item['type']] = item['name']

            result = []
            for k in sorted(extract.keys()):
                result.append(extract[k])

            fields = ['country', 'admin_level1', 'admin_level2', 'admin_level3']

            num_items = len(result) if len(result) <= 4 else 4

            for i in range(num_items):
                setattr(self, fields[i], result[i])

            if save:
                self.save()


    def update_stats(self, value = 1):
        if hasattr(self.user, 'dateo_count'):
            self.user.dateo_count += value
            self.user.save()

        if self.tags.count() > 0:
            for tag in self.tags.all():
                tag.dateo_count += value
                if self.has_images():
                    tag.image_count += value
                if self.has_files():
                    tag.file_count += value
                tag.save()

            campaigns = Campaign.objects.filter(main_tag__in=self.tags.all())
            for c in campaigns:
                if hasattr(c, 'dateo_count'):
                    c.dateo_count += value
                    c.save()
                    cache.delete('campaign.'+str(c.pk))

    def refresh_stats(self, published_changed):

        if self.published and not published_changed:
            add_tags = []
            del_tag_pks = []
            current_tag_pks = [t.pk for t in self.tags.all()]
            # new tags:
            for tag in self.tags.all():
                if tag.pk not in self._prev_tag_pks:
                    add_tags.append(tag)

            for pk in self._prev_tag_pks:
                if pk not in current_tag_pks:
                    del_tag_pks.append(pk)

            if len(add_tags) > 0:
                # modify new tags
                for tag in add_tags:
                    tag.dateo_count += 1
                    if self.has_images():
                        tag.image_count += 1
                    if self.has_files():
                        tag.file_count += 1
                    tag.save()

                # modfiy new campaigns
                new_campaigns = Campaign.objects.filter(main_tag__in=add_tags)
                for c in new_campaigns:
                    if hasattr(c, 'dateo_count'):
                        c.dateo_count += 1
                        c.save()
                        cache.delete('campaign.'+str(c.pk))

            if len(del_tag_pks) > 0:
                del_tags = Tag.objects.filter(pk__in=del_tag_pks)
                for tag in del_tags:
                    tag.dateo_count -= 1
                    if self.has_images():
                        tag.image_count -= 1
                    if self.has_files():
                        tag.file_count -= 1
                    tag.save()

                # modfiy deleted campaigns
                del_campaigns = Campaign.objects.filter(main_tag__in=del_tags)
                for c in del_campaigns:
                    if hasattr(c, 'dateo_count'):
                        c.dateo_count -= 1
                        c.save()
                        cache.delete('campaign.'+str(c.pk))

        elif self.published and published_changed:
            self.update_stats(1)

        elif not self.published and published_changed:
            del_tags = Tag.objects.filter(pk__in=self._prev_tag_pks)
            for tag in del_tags:
                tag.dateo_count -= 1
                if self.has_images():
                    tag.image_count -= 1
                if self.has_files():
                    tag.file_count -= 1
                tag.save()

            # modfiy deleted campaigns
            del_campaigns = Campaign.objects.filter(main_tag__in=del_tags)
            for c in del_campaigns:
                if hasattr(c, 'dateo_count'):
                    c.dateo_count -= 1
                    c.save()
                    cache.delete('campaign.'+str(c.pk))

    class Meta:
        verbose_name = 'Dateo'
        verbose_name_plural = 'Dateos'



class DateoStatus(models.Model):

    user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User")
    created = models.DateTimeField('created', auto_now_add=True)
    modified = models.DateTimeField('modified', auto_now=True)
    status_choices = (
        ('new','new'),
        ('reviewed', 'reviewed'),
        ('solved', 'solved')
    )
    status = models.CharField("status", max_length=15, choices=status_choices, default="new")
    dateo = models.ForeignKey('Dateo', verbose_name='Dateo', related_name="admin")
    campaign = models.ForeignKey(Campaign, verbose_name='Campaign', related_name="admin")

    class Meta:
        verbose_name = 'Dateo status'
        verbose_name_plural = 'Dateo statuses'
        unique_together = ("campaign", "dateo")


class Redateo(models.Model):

    user =  models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User")
    dateo = models.ForeignKey('Dateo', verbose_name='Dateo', related_name="redateos")
    created = models.DateTimeField('created', auto_now_add=True)
    tags = models.ManyToManyField(Tag, verbose_name="Tags", related_name="redateos");

    class Meta:
        verbose_name = 'Redateo'
        verbose_name_plural = 'Redateos'
        unique_together = ("user", "dateo")

    def update_stats(self, value):
        self.dateo.redateo_count += value
        self.dateo.save()

# importing here to aavoid circular imports
from dateo.search_indexes import DateoIndex, RedateoIndex
from api.signals import resource_saved, resource_pre_saved
from django.db.models.signals import pre_delete, post_delete
from notify.models import ActivityLog

# KEEP HAYSTACK INDEX UP TO DATE IN REALTIME
# AND UPDATE DATEO STATS AFTER API RESOURCE SAVED (WITH ALL M2M FIELDS)
# -> only happens with calls to the api (tastypie)
def before_dateo_saved(sender, instance, created, **kwargs):
    if hasattr(instance, 'user') and hasattr(instance, 'tags') and instance.tags.count() >0:
        instance._prev_tag_pks = [t.pk for t in instance.tags.all()]
    else:
        instance._prev_tag_pks = []

def after_dateo_saved(sender, instance, created, **kwargs):
    if created:
        instance.update_stats(1)
    else:
        cache.delete('dateo.'+str(instance.pk))
        published_changed = instance.published != instance._orig_published
        instance.refresh_stats(published_changed)
        for redateo in instance.redateos.all():
            RedateoIndex().update_object(redateo)
    DateoIndex().update_object(instance)

def before_dateo_delete(sender, instance, **kwargs):
    instance.deleting = True
    cache.delete('dateo.'+str(instance.pk))
    DateoIndex().remove_object(instance)
    instance.redateos.all().delete()
    instance.update_stats(-1)
    ActivityLog.objects.filter(action_key='dateo.'+str(instance.pk)).delete()
    Follow.objects.filter(content_type__model="dateo", object_id=instance.pk).delete()

resource_pre_saved.connect(before_dateo_saved, sender=Dateo, dispatch_uid="dateo.pre_save")
resource_saved.connect(after_dateo_saved, sender=Dateo, dispatch_uid="dateo.saved")
pre_delete.connect(before_dateo_delete, sender=Dateo, dispatch_uid="dateo.delete")

def after_status_saved(sender, instance, created, **kwargs):
    DateoIndex().update_object(instance.dateo)

def after_status_delete(sender, instance, **kwargs):
    DateoIndex().update_object(instance.dateo)

resource_saved.connect(after_status_saved, sender=DateoStatus, dispatch_uid="dateoStatus.saved")
post_delete.connect(after_status_delete, sender=DateoStatus, dispatch_uid="dateoStatus.delete")

def after_redateo_saved(sender, instance, created, **kwargs):
    instance.update_stats(1)
    DateoIndex().update_object(instance.dateo)
    RedateoIndex().update_object(instance)

def after_redateo_delete(sender, instance, **kwargs):
    instance.update_stats(-1)
    ActivityLog.objects.filter(action_key='redateo.'+str(instance.pk)).delete()
    if instance.dateo and not hasattr(instance.dateo, 'deleting'):
        DateoIndex().update_object(instance.dateo)
    RedateoIndex().remove_object(instance)

resource_saved.connect(after_redateo_saved, sender=Redateo, dispatch_uid="redateo.saved")
post_delete.connect(after_redateo_delete, sender=Redateo, dispatch_uid="redateo.delete")
