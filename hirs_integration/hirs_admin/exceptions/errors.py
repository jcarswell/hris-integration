from common.exceptions import HrisIntegrationBaseError

class HrisAdminBaseError(HrisIntegrationBaseError):
    pass


class RenderError(HrisAdminBaseError):
    """Thrown when the system encouters an error with rendering a
        portion of a page."""
    pass