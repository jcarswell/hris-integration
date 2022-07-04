# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.api.serializers import Select2Serializer, Select2Meta
from rest_framework.serializers import ModelSerializer

from ftp_import import models


class FileTracking(ModelSerializer):
    class Meta:
        model = models.FileTrack
        fields = "__all__"
