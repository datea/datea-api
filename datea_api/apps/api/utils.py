from .models import ApiConfig
from django.conf import settings 
import unicodedata

def get_reserved_usernames():
	return settings.RESERVED_USERNAMES + ApiConfig.get_solo().reserved_usernames.split(',')




