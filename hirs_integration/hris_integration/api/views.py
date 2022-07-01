# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import OrderedDict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


class APIRootView(APIView):
    swagger_schema = None
    exclude_from_schema = True

    def get_view_name(self):
        return "HRIS Integration API Root"

    def get(self, request, format=None):
        return Response(
            OrderedDict(
                (
                    (
                        "employee",
                        reverse(
                            "employee_api:api-root", request=request, format=format
                        ),
                    ),
                    (
                        "organization",
                        reverse(
                            "organization_api:api-root", request=request, format=format
                        ),
                    ),
                    (
                        "user_applications",
                        reverse(
                            "user_applications_api:api-root",
                            request=request,
                            format=format,
                        ),
                    ),
                    (
                        "smtp_client",
                        reverse(
                            "smtp_client_api:api-root", request=request, format=format
                        ),
                    ),
                    # ('settings', reverse('settings:api-root',
                    #                     request=request,
                    #                     format=format)),
                    (
                        "ftp_import",
                        reverse(
                            "ftp_import_api:api-root", request=request, format=format
                        ),
                    ),
                    (
                        "extras",
                        reverse("extras_api:api-root", request=request, format=format),
                    ),
                    (
                        "_s2_employee",
                        reverse("employee_s2:api-root", request=request, format=format),
                    ),
                    (
                        "_s2_organization",
                        reverse(
                            "organization_s2:api-root", request=request, format=format
                        ),
                    ),
                    (
                        "_s2_user_applications",
                        reverse(
                            "user_applications_s2:api-root",
                            request=request,
                            format=format,
                        ),
                    ),
                    (
                        "_s2_smtp_client",
                        reverse(
                            "smtp_client_s2:api-root", request=request, format=format
                        ),
                    ),
                    # ('_s2_settings', reverse('_s2_settings:api-root',
                    #                     request=request,
                    #                     format=format)),
                    (
                        "_s2_extras",
                        reverse("extras_s2:api-root", request=request, format=format),
                    ),
                )
            )
        )
