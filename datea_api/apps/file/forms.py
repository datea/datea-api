from django import forms
from django.utils.translation import ugettext_lazy as _

# use a form mainly to validate incoming data 
class FileUploadForm(forms.Form):
     
     file = forms.FileField(label=_('File'))
     order = forms.IntegerField()