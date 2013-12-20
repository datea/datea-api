from django.contrib import admin
from .models import Dateo

# Register your models here.

class DateoAdmin(admin.ModelAdmin):
    model = Dateo
    readonly_fields = ('vote_count', 'comment_count', 'follow_count')

admin.site.register(Dateo, DateoAdmin)