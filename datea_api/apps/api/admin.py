from django.contrib import admin
from solo.admin import SingletonModelAdmin
from api.models import ApiConfig

admin.site.register(ApiConfig, SingletonModelAdmin)
