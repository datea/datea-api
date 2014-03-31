from haystack import indexes
from .models import Tag

class TagIndex(indexes.SearchIndex, indexes.Indexable):
    
    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/tag/tag_index.txt")
    tag = indexes.CharField(model_attr="tag", faceted=True)
    title = indexes.CharField(model_attr="title", null=True)
    obj_id = indexes.IntegerField(model_attr='pk')
    follow_count = indexes.IntegerField(model_attr="follow_count")
    dateo_count = indexes.IntegerField(model_attr="dateo_count")

    tag_auto = indexes.NgramField(model_attr='tag')

    def get_model(self):
    	return Tag

    def index_queryset(self, using=None):
        return self.get_model().objects.all()