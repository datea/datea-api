import unicodedata
from types import UnicodeType

def remove_accents(s):
	if type(s) == UnicodeType:
		return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
	else:
		return u''

	#striped = u"".join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
	#result = u""
	#for i in range(len(s)):
	#	if striped[i].lower() in [u'a',u'e',u'i',u'o',u'u']:
	#		result += striped[i]
	#	else:
	#		result += s[i]
	#return result