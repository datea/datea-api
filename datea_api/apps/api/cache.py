import json
from django.conf import settings
from tastypie.cache import NoCache
from api.serializers import UTCSerializer
from django.core.cache import cache
import sys

class SimpleDictCache(NoCache):
    """
    Uses Django's current ``CACHES`` configuration to store cached data.
    """

    def __init__(self, cache_name='default', timeout=None, public=None,
                 private=None, *args, **kwargs):
        """
        Optionally accepts a ``timeout`` in seconds for the resource's cache.
        Defaults to ``60`` seconds.
        """
        super(SimpleDictCache, self).__init__(*args, **kwargs)
        self.serializer = UTCSerializer()
        self.timeout = timeout or self.cache.default_timeout
        self.public = public
        self.private = private

    def get(self, key, **kwargs):
        """
        Gets a key from the cache. Returns ``None`` if the key is not found.
        """
        return cache.get(key, **kwargs)

    def set(self, key, value, timeout=None):
        """
        Sets a key-value in the cache.

        Optionally accepts a ``timeout`` in seconds. Defaults to ``None`` which
        uses the resource's default timeout.
        """
        data = self.serializer.to_simple(value, {})
        if timeout is None:
            timeout = self.timeout
        #cache.set(key, data, timeout)
        cache.set(key, data, 3600)
        return data

    def delete(self, key):
        cache.delete(key)

    def cache_control(self):
        control = {
            'max_age': self.timeout,
            's_maxage': self.timeout,
        }

        if self.public is not None:
            control["public"] = self.public

        if self.private is not None:
            control["private"] = self.private

        return control
