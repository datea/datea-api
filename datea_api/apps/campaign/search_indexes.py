from haystack import indexes
from campaign.models import Campaign
import unicodedata

class CampaignIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/campaign/campaign_index.txt")
    obj_id = indexes.IntegerField(model_attr='pk')
    name = indexes.CharField(model_attr='name', boost=1.25)
    slug = indexes.CharField(model_attr='slug', faceted=True)
    user = indexes.CharField(model_attr='user__username', faceted=True)
    user_id = indexes.IntegerField(model_attr="user__pk")
    category = indexes.CharField(model_attr='category__name', null=True, faceted=True)
    category_id = indexes.IntegerField(null=True)
    published = indexes.BooleanField(model_attr='published', null=True)
    featured = indexes.IntegerField(model_attr='featured', null=True)
    created = indexes.DateTimeField(model_attr='created')
    modified = indexes.DateTimeField(model_attr='modified')
    main_tag = indexes.CharField(boost=1.25, faceted=True)
    main_tag_id = indexes.IntegerField()
    secondary_tags = indexes.MultiValueField(boost=1.125, null=True)
    is_active = indexes.CharField()
    center = indexes.LocationField(model_attr='center', null=True)
    dateo_count = indexes.IntegerField(model_attr='dateo_count', null=True)
    follow_count = indexes.IntegerField(model_attr='follow_count', null=True)
    is_standalone = indexes.BooleanField(default=True)
    follow_key = indexes.CharField()
    rank = indexes.IntegerField(model_attr="rank")
    search_auto = indexes.EdgeNgramField()
    #comment_count = indexes.IntegerField(model_attr='comment_count', null=True)
    #user_count = indexes.IntegerField(model_attr='user_count', null=True)

    def get_model(self):
        return Campaign

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_name(self, obj):
        return unicodedata.normalize('NFKD', obj.name).encode('ascii', 'ignore')

    def prepare_main_tag_id(self, obj):
        return obj.main_tag.id

    def prepare_main_tag(self, obj):
        return obj.main_tag.tag.lower()

    def prepare_is_active(self, obj):
        return obj.is_active()

    def prepare_secondary_tags(self, obj):
        return [obj.main_tag.tag.lower()] + [tag.tag.lower() for tag in obj.secondary_tags.all()]

    def prepare_category_id(self, obj):
        if obj.category:
            return int(obj.category.pk)
        else:
            return None

    def prepare_follow_key(self, obj):
        return 'tag.'+str(obj.main_tag.pk)

    def prepare_search_auto(self, obj):
      return obj.name.lower() + ' ' + obj.main_tag.tag.lower()+ ' #' + obj.main_tag.tag.lower()
