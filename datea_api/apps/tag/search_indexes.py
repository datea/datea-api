from haystack import indexes
from models import Tag

class TagIndex(indexes.SearchIndex, indexes.Indexable):
    
    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/tag/tag_index.txt")
    obj_id = indexes.IntegerField(model_attr='pk')
    tag_auto = indexes.NgramField(model_attr='tag')

    def get_model(self):
    	return Tag

    def index_queryset(self, using=None):
        return self.get_model().objects.all()