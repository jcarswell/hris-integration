# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.http import HttpResponseRedirect


class AuthRequiredMiddleware:
    EXEMPT_PATHS = [
        "/accounts/login/",
        "/api/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and not request.path_info.startswith(
            self.EXEMPT_PATHS
        ):
            return self.get_response(request)
        else:
            return HttpResponseRedirect(f"/accounts/login/?next={request.path}")
