# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.urls import path
from hris_integration.views import FormView, ListView

from . import forms

urlpatterns = [
    path("jobs/", ListView.as_view(form=forms.JobRole), name="jobs"),
    path("jobs/<int:id>/", FormView.as_view(form=forms.JobRole), name="jobs_edit"),
    path(
        "businessunits/",
        ListView.as_view(form=forms.BusinessUnit),
        name="business_units",
    ),
    path(
        "businessunits/<int:id>/",
        FormView.as_view(form=forms.BusinessUnit),
        name="business_units_edit",
    ),
    path("locations/", ListView.as_view(form=forms.Location), name="location"),
    path(
        "locations/<int:id>/",
        FormView.as_view(form=forms.Location),
        name="location_edit",
    ),
    path(
        "settings/admapping/",
        ListView.as_view(form=forms.GroupMapping),
        name="group_mappings",
    ),
    path(
        "settings/admapping/<int:id>/",
        FormView.as_view(form=forms.GroupMapping),
        name="group_mappings_edit",
    ),
]
