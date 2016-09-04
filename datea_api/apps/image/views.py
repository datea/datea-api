import sys
import json
from image.models import Image
from forms import ImageUploadForm
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from resources import ImageResource
from tastypie.authentication import ApiKeyAuthentication

@csrf_exempt
def save_image(request):
    """
    Save DateaImage instance for specified object FK or M2M-Field
    post parameters must include:
        image:           image file input 
        order:           the order of the image (optional)
    """
    key_auth = ApiKeyAuthentication()

    if not key_auth.is_authenticated(request):
        return HttpResponse("<h1>Login required</h1>")

    form = ImageUploadForm(request.POST, request.FILES)

    if form.is_valid():

        image_data = request.FILES['image']
        image_instance = Image(image=image_data, user=request.user)
        if 'order' in form.cleaned_data:
            image_instance.order = form.cleaned_data['order']
        image_instance.save()

        # create image resource
        ir = ImageResource()
        im_bundle = ir.build_bundle(obj=image_instance)
        im_bundle = ir.full_dehydrate(im_bundle)

        data = {'ok': True, 'message':'ok', 'resource': im_bundle.data}
        data = json.dumps(data)

    else:
        data = json.dumps({'ok': False, 'message': form.errors})

    return HttpResponse(data, mimetype="application/json")


