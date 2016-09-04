from django.contrib import admin
from .models import Tag

class TagAdmin(admin.ModelAdmin):
    search_fields = ['tag']
    model = Tag

admin.site.register(Tag, TagAdmin)
