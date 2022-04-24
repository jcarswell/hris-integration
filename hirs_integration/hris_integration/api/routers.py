# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from rest_framework import routers

class S2Router(routers.DefaultRouter):
    """A simplified router for select2 ajax calls."""

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