import sys
import json
from dateo.models import File
from file.forms import FileUploadForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dateo.resources import FileResource
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
          file_instance.order = form.cleaned_data['order']
        if 'title' in form.cleaned_data:
            file_instance.title = form.cleaned_data['title']
        file_instance.save()

        # create image resource
        fr = FileResource()
        f_bundle = fr.build_bundle(obj=file_instance)
        f_bundle = fr.full_dehydrate(f_bundle)

        data = {'ok': True, 'message':'ok', 'resource': f_bundle.data}
        status = 201
    else:
        data = {'ok': False, 'message': form.errors}
        status = 400

    resp = JsonResponse(data)
    resp.status_code = status
    return resp
