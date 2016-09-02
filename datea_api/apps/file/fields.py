from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
import magic

allowed_extensions = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pps', 'pptx', 'ppsx',
                      'odt', 'fodt', 'ods', 'fods', 'odp', 'fodp', 'odg', 'fodg',
                      'json', 'csv', 'xml', 'kml', 'rdf',
                      'pdf', 'ps', 'rtf', 'txt',
                      'zip', 'gzip',
                      'mp3', 'mp4', 'ogg'
                     ]

allowed_mimetypes = ['application/msword',
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'application/vnd.ms-excel',
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     'application/vnd.ms-powerpoint',
                     'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                     'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
                     'application/vnd.oasis.opendocument.text',
                     'application/vnd.oasis.opendocument.spreadsheet',
                     'application/vnd.oasis.opendocument.presentation',
                     'application/vnd.oasis.opendocument.graphics',
                     'application/json',
                     'application/xml',
                     'text/csv',
                     'text/plain',
                     'text/rtf',
                     'text/xml',
                     'application/pdf',
                     'application/postscript',
                     'application/rdf+xml',
                     'application/zip',
                     'application/gzip',
                     'audio/mpeg',
                     'audio/mp4',
                     'audio/ogg'
                    ]

class ContentTypeRestrictedFileField(FileField):

    def __init__(self, *args, **kwargs):
        #self.file_extensions = kwargs.pop("file_extensions")
        #self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)


    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        try:
            ext = data.file.name.split(".")[-1].lower()
            if ext in allowed_extensions:
                if data.file._size > 10485760:
                    raise forms.ValidationError('Please keep filesize under 10MB. Current filesize %s' % filesizeformat(data.file._size))

                if not magic.form_buffer(data.file, mime=True) in allowed_mimetypes:
                    raise forms.ValidationError('Filetype not supported.')
            else:
                raise forms.ValidationError('Filetype not supported.')
        except AttributeError:
            pass

        return data
