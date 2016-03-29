from haystack import indexes
from tag.models import Tag

class TagIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/tag/tag_index.txt")
    tag = indexes.CharField(model_attr="tag", faceted=True)
    title = indexes.CharField(model_attr="title", null=True)
    obj_id = indexes.IntegerField(model_attr='pk')
    follow_count = indexes.IntegerField(model_attr="follow_count")
    dateo_count = indexes.IntegerField(model_attr="dateo_count")
    is_standalone = indexes.BooleanField()
    follow_key = indexes.CharField()
    rank = indexes.IntegerField(model_attr="rank")
    published = indexes.BooleanField()
    tag_auto = indexes.NgramField(model_attr='tag')

    def get_model(self):
    	return Tag

    def prepare_tag(self, obj):
        return obj.tag.lower()

    def prepare_is_standalone(self, obj):
        return not obj.campaigns.count() and not obj.campaigns_secondary.count()

    def prepare_published(self, obj):
        return True

    def prepare_follow_key(self, obj):
        return 'tag.'+str(obj.pk)

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
