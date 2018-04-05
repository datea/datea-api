from haystack import indexes
from account.models import User

class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/indexes/account/user_index.txt")
    content_auto = indexes.EdgeNgramField(model_attr='username')

    def get_model(self):
        return User
