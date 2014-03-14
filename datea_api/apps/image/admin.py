from django.contrib import admin
from .models import Image

class ImageAdmin(admin.ModelAdmin):
    model = Image

admin.site.register(Image, ImageAdmin)
