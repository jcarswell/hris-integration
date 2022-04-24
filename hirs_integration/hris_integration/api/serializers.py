# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from collections import OrderedDict
from rest_framework.serializers import ModelSerializer

class Select2Meta:
        #: str: The name of the primary key field, defaults to 'id'.
        field_id = 'id'
        #: list: The name of the field(s) to use for the label, must be defined.
        field_text = None

        fields = [field_id] + field_text
        read_only_fields = fields


class Select2Serializer(ModelSerializer):
    """The base class for all select2 serializers"""

    def to_representation(self, instance) -> OrderedDict:
        """Returns a ordered dict int the format specified by select2"""

        data = super().to_representation(instance)
        ret = OrderedDict()
        ret["id"] = f"id_{getattr(instance, self.field_id)}"
        ret["text"] = " ".join([getattr(instance, field) for field in self.field_text])
        return data