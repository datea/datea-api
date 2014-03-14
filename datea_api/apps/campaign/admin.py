from django.contrib import admin
from .models import Campaign

class CampaignAdmin(admin.ModelAdmin):
    model = Campaign
    readonly_fields = ('dateo_count', 'comment_count', 'follow_count')

admin.site.register(Campaign, CampaignAdmin)