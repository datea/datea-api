from django import forms

# use a form mainly to validate incoming data
class FileUploadForm(forms.Form):
    file = forms.FileField(label='File')
    order = forms.IntegerField(required=False)
    title = forms.CharField(required=False, max_length=128)
