from django.dispatch import Signal

resource_saved = Signal(providing_args=['instance', 'created'])