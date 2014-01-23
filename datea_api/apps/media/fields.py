from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from lxml import objectify
from PyPDF2 import PdfFileReader

class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        #self.file_extensions = kwargs.pop("file_extensions")
        #self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):        
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        
        try:
            ext = data.file.name.split(".")[-1].lower()
            if ext in ['kml', 'pdf']:
                if file._size > 10485760:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
                
                # validate kml file
                if ext == 'kml':
                    try:
                        # Google own generated kml doesn't pass real kml validation with a schema,
                        # so we just open it with lxml and see if its valid xml for now
                        objectify.parse(data.file)
                    except:
                        raise forms.ValidationError(_('Not a valid kml file'))

                # validate pdf files
                elif ext == 'pdf':
                    try:
                        # open pdf with pypdf2, if no errors, its valid (not a perfect test, but...)
                        PdfFileReader(data.file)
                    except:
                        raise forms.ValidationError(_('Not a valid pdf file'))

            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass        
            
        return data

