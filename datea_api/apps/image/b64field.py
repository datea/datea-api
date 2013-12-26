import base64
import os
from tastypie.fields import FileField
from django.core.files.uploadedfile import SimpleUploadedFile

class Base64FileField(FileField):
    """
    A django-tastypie field for handling file-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file.
    Usage:

    class MyResource(ModelResource):
        file_field = Base64FileField("file_field")
        
        class Meta:
            queryset = ModelWithFileField.objects.all()

    In the case of multipart for submission, it would also pass the filename.
    By using a raw post data stream, we have to pass the filename within our
    file_field structure:

    file_field = {
        "name": "myfile.png",
        "data": "longbas64encodedstring",
        "content_type": "image/png" # on hydrate optional
    }
    """
    def dehydrate(self, bundle, for_list=True):

        instance = getattr(bundle.obj, self.instance_name, None)
        try:
            url = getattr(instance, 'url', None)
        except ValueError:
            url = None
        return url

        '''
        if not bundle.data.has_key(self.instance_name) and hasattr(bundle.obj, self.instance_name):
            file_field = getattr(bundle.obj, self.instance_name)
            if file_field:
                try:
                    content_type, encoding = mimetypes.guess_type(file_field.file.name)
                    b64 = open(file_field.file.name, "rb").read().encode("base64")
                    ret = {
                        "name": os.path.basename(file_field.file.name),
                        "file": b64,
                        "content-type": content_type or "application/octet-stream"
                    }
                    return ret
                except:
                    pass
        return None
        '''

    def hydrate(self, obj):
        value = super(FileField, self).hydrate(obj)
        if value:
            b64_string, mime_type = datauri_decode(value['file']['data_uri'])
            file_field = {
                "name": value['file']['name'],
                "data": b64_string,
                "content_type": mime_type,
            }
            value = SimpleUploadedFile(value["name"], base64.b64decode(fiel_field), getattr(value, "content_type", "application/octet-stream"))
        return value


    def datauri_decode(data_url):
        metadata, encoded = data_url.rsplit(b(","), 1)
        mime_type = metadata.split(';')[0].split(':')[1]
        return b64_string, mime_type

