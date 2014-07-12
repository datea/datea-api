from django.db.models import signals
from django.dispatch import Signal
from haystack.signals import BaseSignalProcessor

from datea_api.apps.dateo.models import Dateo
from datea_api.apps.tag.models import Tag
from datea_api.apps.campaign.models import Campaign
from datea_api.apps.notify.models import ActivityLog

# RESOURCE SAVED SIGNAL
resource_saved = Signal(providing_args=['instance', 'created'])