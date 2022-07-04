# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.routers import APIRootView

from . import serializers
from ftp_import import models


class FTPImportRootView(APIRootView):
    def get_view_name(self):
        return "FTP Import"


class FileTrackingView(ModelViewSet):
    queryset = models.FileTrack.objects.all()
    serializer_class = serializers.FileTracking
    permission_classes = [IsAdminUser]
