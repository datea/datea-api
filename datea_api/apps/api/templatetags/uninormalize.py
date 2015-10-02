from django import template
import unicodedata
from types import UnicodeType
register = template.Library()

def uninormalize(val): 
	if type(val) == UnicodeType:
		return unicodedata.normalize('NFKD', val).encode('ascii', 'ignore')
	else:
		return val

register.filter('uninormalize', uninormalize)


