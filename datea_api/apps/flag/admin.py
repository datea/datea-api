from django.contrib import admin
from flag.models import Flag

class FlagAdmin(admin.ModelAdmin):
    model = Flag

admin.site.register(Flag, FlagAdmin)
