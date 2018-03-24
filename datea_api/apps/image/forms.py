from django import forms

# use a form mainly to validate incoming data
class ImageUploadForm(forms.Form):
    image = forms.ImageField(label='Image')
    order = forms.IntegerField(required=False)
