from django.contrib import admin
from .models import Tag

class TagAdmin(admin.ModelAdmin):
    model = Tag

admin.site.register(Tag, TagAdmin)
