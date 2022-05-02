# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from rest_framework.routers import Route,DynamicRoute,SimpleRouter

class S2Router(SimpleRouter):
    """A simplified router for select2 ajax calls. based on the Django REST Framework
    readonly router example."""

    #: str: The leading prefix to use for the select2 ajax calls.
    prefix = '_s2'

    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'get': 'list'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/{lookup}$',
            mapping={'get': 'retrieve'},
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Detail'}
        ),
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        )
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = getattr(kwargs, "prefix", "_s2")

    def register(self, prefix, viewset, base_name=None):
        """Register a viewset with a prefix."""

        if base_name is None:
            base_name = 's2-' + self.get_default_basename(viewset)

        self.registry.append((f"{self.prefix}/{prefix}", viewset, base_name))