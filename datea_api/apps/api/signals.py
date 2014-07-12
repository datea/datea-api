from django.dispatch import Signal

# RESOURCE SAVED SIGNAL
resource_saved = Signal(providing_args=['instance', 'created'])