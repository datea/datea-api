from .models import ApiConfig
from django.conf import settings 
import unicodedata

def get_reserved_usernames():
	result = settings.RESERVED_USERNAMES
	if ApiConfig.get_solo().reserved_usernames:
		result += ApiConfig.get_solo().reserved_usernames.split(',')
	return result



