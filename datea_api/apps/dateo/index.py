from haystack import indexes
from models import Dateo

class MapItemIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    
    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/datea_mapping/dateamapitem_text.txt")
    obj_id = indexes.IntegerField(model_attr='pk')
    user = indexes.CharField(model_attr='user')
    user_id = indexes.IntegerField()
    published = indexes.BooleanField(model_attr='published')
    status = indexes.CharField(model_attr='status', null=True)
    category = indexes.CharField(model_attr='category', null=True)
    category_id = indexes.IntegerField(null=True)
    tags = indexes.MultiValueField()
    position = indexes.LocationField(model_attr='position', null=True)
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    
    
    def get_model(self):
        return Dateo
    
    def index_queryset(self):
        return self.get_model().objects.all()
    
    def prepare_tags(self, obj):
        return ['#'+tag.tag for tag in obj.tags.all()]

    def prepare_user_id(self, obj):
        return int(obj.user.pk)

    def prepare_category_id(self, obj):
        if obj.category:
            return int(obj.category.pk)
        else:
            return None