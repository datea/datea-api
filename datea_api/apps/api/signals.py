from django.db.models import signals
from django.dispatch import Signal
from haystack.signals import BaseSignalProcessor

from datea_api.apps.dateo.models import Dateo
from datea_api.apps.tag.models import Tag
from datea_api.apps.campaign.models import Campaign
from datea_api.apps.notify.models import ActivityLog

# RESOURCE SAVED SIGNAL
resource_saved = Signal(providing_args=['instance', 'created'])

# CUSTOM HAYSTACK SIGNAL PROCESSOR -> handle m2m cases [TODO: figure out how to avoid doubble saves]
class DateaIndexSignalProcessor(BaseSignalProcessor):

    def setup(self):
    	# Dateos
    	signals.m2m_changed.connect(self.handle_save, sender=Dateo)
        signals.post_save.connect(self.handle_save, sender=Dateo)
       	signals.post_delete.connect(self.handle_delete, sender=Dateo)

        # Campaigns
        signals.m2m_changed.connect(self.handle_save, sender=Campaign)
        signals.post_save.connect(self.handle_save, sender=Campaign)
       	signals.post_delete.connect(self.handle_delete, sender=Campaign)

       	# Tags
       	signals.m2m_changed.connect(self.handle_save, sender=Tag)
        signals.post_save.connect(self.handle_save, sender=Tag)
       	signals.post_delete.connect(self.handle_delete, sender=Tag)

       	# ActivityLogs
       	signals.m2m_changed.connect(self.handle_save, sender=ActivityLog)
        signals.post_save.connect(self.handle_save, sender=ActivityLog)
       	signals.post_delete.connect(self.handle_delete, sender=ActivityLog)


    def teardown(self):
        
        # Dateos
    	signals.m2m_changed.disconnect(self.handle_save, sender=Dateo)
        signals.post_save.disconnect(self.handle_save, sender=Dateo)
       	signals.post_delete.disconnect(self.handle_delete, sender=Dateo)

        # Campaigns
        signals.m2m_changed.disconnect(self.handle_save, sender=Campaign)
        signals.post_save.disconnect(self.handle_save, sender=Campaign)
       	signals.post_delete.disconnect(self.handle_delete, sender=Campaign)

       	# Tags
       	signals.m2m_changed.disconnect(self.handle_save, sender=Tag)
        signals.post_save.disconnect(self.handle_save, sender=Tag)
       	signals.post_delete.disconnect(self.handle_delete, sender=Tag)

       	# ActivityLogs
       	signals.m2m_changed.disconnect(self.handle_save, sender=ActivityLog)
        signals.post_save.disconnect(self.handle_save, sender=ActivityLog)
       	signals.post_delete.disconnect(self.handle_delete, sender=ActivityLog)
