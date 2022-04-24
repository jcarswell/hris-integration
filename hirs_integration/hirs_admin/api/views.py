from rest_framework.routers import APIRootView

class HirsAdminRootView(APIRootView):
    """
    Root view for the HRIS Admin API.
    """
    def get_view_name(self):
        return "HRIS Admin API"

