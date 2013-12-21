from django import forms
from django.utils.translation import ugettext_lazy as _

# use a form mainly to validate incoming data 
class ImageUploadForm(forms.Form):
     
     image = forms.ImageField(label=_('Image'))
     thumb_preset = forms.CharField(label=_('Thumb preset'), widget=forms.HiddenInput(), required=False)