from django.contrib import admin
from follow.models import Follow

class FollowAdmin(admin.ModelAdmin):
    model = Follow

admin.site.register(Follow, FollowAdmin)
