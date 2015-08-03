from tastypie.serializers import Serializer
from tastypie.utils import format_datetime, make_naive
import datetime

class UTCSerializer(Serializer):

	def format_datetime(self, data):
		"""
		A hook to control how datetimes are formatted.

		Can be overridden at the ``Serializer`` level (``datetime_formatting``)
		or globally (via ``settings.TASTYPIE_DATETIME_FORMATTING``).

		Default is ``iso-8601``, which looks like "2010-12-16T03:02:14".
		"""
		data = make_naive(data)

		if self.datetime_formatting == 'rfc-2822':
			return format_datetime(data)
		if self.datetime_formatting == 'iso-8601-strict':
			# Remove microseconds to strictly adhere to iso-8601
			data = data - datetime.timedelta(microseconds = data.microsecond)

		# ADD Z to signal it's UTC time!
		return data.isoformat()+'Z'