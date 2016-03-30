from haystack import indexes
from dateo.models import Dateo, Redateo

class DateoIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/dateo/dateo_index.txt")
    obj_id = indexes.IntegerField(model_attr='pk')
    user = indexes.CharField(model_attr='user__username', faceted=True)
    user_id = indexes.IntegerField(model_attr='user__pk')
    published = indexes.BooleanField(model_attr='published')
    status = indexes.CharField(model_attr='status', null=True)
    category = indexes.CharField(model_attr='category__name', null=True, faceted=True)
    category_id = indexes.IntegerField(null=True)
    tags = indexes.MultiValueField(boost=1.125, null=True, faceted=True)
    position = indexes.LocationField(model_attr='position', null=True)
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    date = indexes.DateTimeField(model_attr='date')

    country = indexes.CharField(model_attr='country', null=True)
    admin_level1 = indexes.CharField(model_attr='admin_level1', null=True)
    admin_level2 = indexes.CharField(model_attr='admin_level2', null=True)
    admin_level3 = indexes.CharField(model_attr='admin_level3', null=True)

    redateos = indexes.MultiValueField(null=True)
    admin = indexes.MultiValueField(null=True, faceted=True)

    vote_count = indexes.IntegerField(model_attr="vote_count")
    comment_count = indexes.IntegerField(model_attr="comment_count")
    redateo_count = indexes.IntegerField(model_attr="redateo_count")
    has_images = indexes.BooleanField()
    is_geolocated = indexes.BooleanField()

    def get_model(self):
        return Dateo

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_tags(self, obj):
        tags = [tag.tag.lower() for tag in obj.tags.all()]
        for redateo in obj.redateos.all():
            tags += [tag.tag.lower() for tag in redateo.tags.all()]
        return tags

    def prepare_category_id(self, obj):
        if obj.category:
            return int(obj.category.pk)
        else:
            return None

    def prepare_has_images(self, obj):
        return obj.images.count() > 0

    def prepare_is_geolocated(self, obj):
        return obj.position != None

    def prepare_admin(self, obj):
        return [a.status+':'+str(a.campaign.id) for a in obj.admin.all()]

    def prepare_redateos(self, obj):
        return [redat.user.id for redat in obj.redateos.all()]


class RedateoIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/dateo/redateo_index.txt")
    obj_id = indexes.IntegerField(model_attr='pk')
    user = indexes.CharField(model_attr='user__username', faceted=True)
    user_id = indexes.IntegerField(model_attr='user__pk')
    published = indexes.BooleanField()
    status = indexes.CharField(null=True)
    category = indexes.CharField(null=True, faceted=True)
    category_id = indexes.IntegerField(null=True)
    tags = indexes.MultiValueField(boost=1.125, null=True, faceted=True)
    position = indexes.LocationField(null=True)
    created = indexes.DateTimeField(model_attr='created')
    date = indexes.DateTimeField(null=True)

    country = indexes.CharField(null=True)
    admin_level1 = indexes.CharField(null=True)
    admin_level2 = indexes.CharField(null=True)
    admin_level3 = indexes.CharField(null=True)

    redateos = indexes.MultiValueField(null=True)
    admin = indexes.MultiValueField(null=True, faceted=True)

    vote_count = indexes.IntegerField()
    comment_count = indexes.IntegerField()
    redateo_count = indexes.IntegerField()
    has_images = indexes.BooleanField()
    is_geolocated = indexes.BooleanField()

    def get_model(self):
        return Redateo

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_published(self, obj):
        return obj.dateo.published

    def prepare_status(self, obj):
        return obj.dateo.status

    def prepare_category(self, obj):
        return obj.dateo.category or None

    def prepare_tags(self, obj):
        tags = [tag.tag.lower() for tag in obj.dateo.tags.all()]
        tags += [tag.tag.lower() for tag in obj.tags.all()]
        return tags

    def prepare_category_id(self, obj):
        if obj.dateo.category:
            return int(obj.dateo.category.pk)
        else:
            return None

    def prepare_position(self, obj):
        if obj.dateo.position:
            return '%s,%s' % (obj.dateo.position.y, obj.dateo.position.x)
        else:
            return None

    def prepare_date(self, obj):
        return obj.dateo.date

    def prepare_country(self, obj):
        return obj.dateo.country

    def prepare_admin_level1(self, obj):
        return obj.dateo.admin_level1

    def prepare_admin_level2(self, obj):
        return obj.dateo.admin_level2

    def prepare_admin_level3(self, obj):
        return obj.dateo.admin_level3

    def prepare_has_images(self, obj):
        return obj.dateo.images.count() > 0

    def prepare_is_geolocated(self, obj):
        return obj.dateo.position != None

    def prepare_admin(self, obj):
        return [a.status+':'+str(a.campaign.id) for a in obj.dateo.admin.all()]

    def prepare_redateos(self, obj):
        return [redat.user.id for redat in obj.dateo.redateos.all()]

    def prepare_vote_count(self, obj):
        return obj.dateo.vote_count

    def prepare_comment_count(self, obj):
        return obj.dateo.comment_count

    def prepare_redateo_count(self, obj):
        return obj.dateo.redateo_count
