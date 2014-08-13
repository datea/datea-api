from haystack import indexes
from .models import Dateo

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

    country = indexes.CharField(model_attr='country', null=True)
    admin_level1 = indexes.CharField(model_attr='admin_level1', null=True)
    admin_level1 = indexes.CharField(model_attr='admin_level1', null=True)
    admin_level1 = indexes.CharField(model_attr='admin_level1', null=True)

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
        return [tag.tag for tag in obj.tags.all()]

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