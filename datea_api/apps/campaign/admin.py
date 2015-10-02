from django.contrib import admin
from campaign.models import Campaign

class CampaignAdmin(admin.ModelAdmin):
	model = Campaign
	search_fields = ['name', 'main_tag__tag']
	readonly_fields = ('dateo_count', 'comment_count', 'follow_count')

admin.site.register(Campaign, CampaignAdmin)