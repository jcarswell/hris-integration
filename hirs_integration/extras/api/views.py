# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.routers import APIRootView

from . import serializers
from extras import models

class ExtrasRootView(APIRootView):
    def get_view_name(self):
        return 'Extras'


class ExtrasS2RootView(APIRootView):
    def get_view_name(self):
        return 'Extras Select2'


class S2Countries(Select2ViewSet):
    queryset = models.Country.objects.all()
    serializer_class = serializers.S2CountriesSerializer
    filterset_fields = ['name','code']


class CountriesView(ReadOnlyModelViewSet):
    queryset = models.Country.objects.all()
    serializer_class = serializers.CountriesSerializer
    filterset_fields = ['name','code']


class S2States(Select2ViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.S2StatesSerializer
    filterset_fields = ['country','type','name','code']


class StatesView(ReadOnlyModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.StatesSerializer
    filterset_fields = ['country','type','name','code']