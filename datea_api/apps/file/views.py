import sys
import json
from .models import File
from .forms import FileUploadForm
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .resources import FileResource
from tastypie.authentication import ApiKeyAuthentication

@csrf_exempt
def save_file(request):
    """
        file:           file input 
        order:          the order of the file (optional)
    """
    
    key_auth = ApiKeyAuthentication()
    
    if not key_auth.is_authenticated(request):
        return HttpResponse("<h1>Login required</h1>")

    form = FileUploadForm(request.POST, request.FILES)

    if form.is_valid():
        
            file_data = request.FILES['file']
            file_instance = File(file=file_data, user=request.user)
            if 'order' in form.cleaned_data:
                image_instance.order = form.cleaned_data['order']
            file_instance.save()
            
            # create image resource
            fr = FileResource()
            f_bundle = fr.build_bundle(obj=file_instance)
            f_bundle = fr.full_dehydrate(f_bundle)
            f_json = fr.serialize(f_bundle)

            data = {'ok': True, 'message':'ok', 'resource': json.loads(f_json)}
            data = json.dumps(data)
             
    else:
        data = json.dumps({'ok': False, 'message': form.errors})

    return HttpResponse(data, mimetype="application/json")


