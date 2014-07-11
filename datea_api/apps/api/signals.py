from django.dispatch import Signal
#from haystack.indexes import RealTimeSearchIndex

resource_saved = Signal(providing_args=['instance', 'created'])
'''
class ManyAwareRealTimeSearchIndex(RealTimeSearchIndex):
    """Many-to-many aware real-time search index base class
    """

    def _on_m2m_changed(self, instance, using=None, **kwargs):
        """Listen for post-action changes to a many-to-many field,
        and (possibly) index and object.
        """

        # ignore any pre-save actions
        if kwargs['action'].startswith('post_'):
            self.update_object(instance, using=using, **kwargs)

    def _setup_save(self, model):
        signals.post_save.connect(self.update_object, sender=model)

        # connect each of the model's many-to-many fields
        # to the m2m change listener
        for m2m in model._meta.many_to_many:
            signals.m2m_changed.connect(self._on_m2m_changed,
                                        sender=m2m.rel.through)

    def _teardown_save(self, model):
        signals.post_save.disconnect(self.update_object, sender=model)

        # disconnect each many-to-many field from the change handler
        for m2m in model._meta.many_to_many:
            signals.m2m_changed.disconnect(self._on_m2m_changed,
                                           sender=m2m.rel.through)
'''