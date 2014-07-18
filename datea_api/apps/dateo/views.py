from .models import Dateo
from datea_api.apps.tag.models import Tag
from .utils import UnicodeWriter
from django.contrib.sites.models import Site
from django.conf import settings
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from datetime import datetime

# Create your views here.

def csv_export_tag(request, tag_id):

	tag = Tag.objects.get(pk=tag_id)
	filename = tag.tag+'_'+datetime.now().strftime('%d-%m-%Y')

	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename="'+filename+'.csv"'

	writer = UnicodeWriter(response)

	meta_row = ['username', 'created', 'tags', 'content', 'date', 'address', 'latitude', 
				 'longitude', 'country', 'admin_level1', 'admin_level2', 'admin_level3', 
				 'images', 'files', 'status', 'vote_count', 'comment_count']
	writer.writerow(meta_row)

	for dateo in Dateo.objects.filter(tags=tag_id, published=True):
		row = make_dateo_csv_row(dateo)
		writer.writerow(row)

	return response


def make_dateo_csv_row(dateo):
	"""
	username, created, tags, content, date, address, latitude, longitude, country, admin_level1, admin_level2, admin_level3, images, files, status, vote_count, comment_count
	"""
	site = Site.objects.get_current()
	host = settings.PROTOCOL+'://'+site.domain

	# position
	lat = ''
	lng = ''
	if dateo.position:
		lat = dateo.position.y
		lng = dateo.position.x

	# images
	images = ''
	if dateo.images.count() > 0:
		images = " ".join([host+img.image.url for img in dateo.images.all()])

	# files
	files = ''
	if dateo.images.count() > 0:
		files = " ".join([host+f.file.url for f in dateo.files.all()])

	return [
		dateo.user.username,
		dateo.created.strftime("%Y-%m-%d %H:%M:%S"),
		" ".join(['#'+t.tag for t in dateo.tags.all()]),
		dateo.content,
		dateo.date.strftime("%Y-%m-%d %H:%M:%S"),
		dateo.address or '',
		str(lat),
		str(lng),
		dateo.country or '',
		dateo.admin_level1 or '',
		dateo.admin_level2 or '',
		dateo.admin_level3 or '',
		images,
		files,
		dateo.status,
		str(dateo.vote_count),
		str(dateo.comment_count),
	]



