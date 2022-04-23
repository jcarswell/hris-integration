from sys import prefix
from rest_framework import routers


class S2Router(routers.DefaultRouter):
    """A simplified router for select2 ajax calls.
    """

    prefix = '_s2'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.routes[0].mapping.keys():
            if key != 'get':
                self.routes[0].mapping.pop(key)

        if "prefix" in kwargs.keys:
            self.prefix = kwargs["prefix"]

    def register(self, prefix, viewset, base_name=None):
        """Register a viewset with a prefix."""

        if base_name is None:
            base_name = self.get_default_base_name(viewset)
        self.registry.append((f"{self.prefix}/{prefix}", viewset, base_name))