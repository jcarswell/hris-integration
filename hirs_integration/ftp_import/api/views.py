# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from . import serializers
from ftp_import import models

class FileTrackingView(ModelViewSet):
    queryset = models.FileTrack.objects.all()
    serializer_class = serializers.FileTracking
    permission_classes = [IsAdminUser]