# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from rest_framework.routers import Route, DefaultRouter
import logging

logger = logging.getLogger("api.router")


class HrisRouter(DefaultRouter):
    def register(self, prefix: str, viewset, basename: str = None):
        """use _ in the name instead of -"""

        if basename is None:
            basename = self.get_default_basename(viewset)

        basename = basename.replace("-", "_")

        logger.debug(f"Registering ({prefix}, {viewset}, {basename})")
        self.registry.append((prefix, viewset, basename))

        # invalidate the urls cache
        if hasattr(self, "_urls"):
            del self._urls


class S2Router(HrisRouter):
    """A simplified router for select2 ajax calls. based on the Django REST Framework
    readonly router example."""

    routes = [
        Route(
            url=r"^{prefix}$",
            mapping={"get": "list"},
            name="s2_{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = getattr(kwargs, "prefix", "_s2")

    def register(self, prefix: str, viewset, basename: str = None):
        """Register a viewset with a prefix."""

        if basename is None:
            basename = self.get_default_basename(viewset)

        basename = basename.replace("-", "_")

        logger.debug(f"Registering ({prefix}, {viewset}, {basename})")
        self.registry.append((prefix, viewset, basename))

        # invalidate the urls cache
        if hasattr(self, "_urls"):
            del self._urls
