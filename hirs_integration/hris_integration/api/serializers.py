# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from collections import OrderedDict
from rest_framework.serializers import ModelSerializer

logger = logging.getLogger("hris_integration.serializers")

class Select2Meta:
        #: str: The name of the primary key field, defaults to 'id'.
        field_id = 'id'
        #: list: The name of the field(s) to use for the label, must be defined.
        field_text = []
        field_text_format = None


class Select2Serializer(ModelSerializer):
    """The base class for all select2 serializers"""

    def to_representation(self, instance) -> OrderedDict:
        """Returns a ordered dict int the format specified by select2"""

        ret = OrderedDict()
        ret["id"] = f"id_{getattr(instance, self.Meta.field_id)}"
        if hasattr(self.Meta,"field_text_format") and self.Meta.field_text_format:
            fields = {field:getattr(instance,field) for field in self.Meta.field_text}
            logger.debug(f"formatting output with fields: {fields}")
            ret["text"] = self.Meta.field_text_format.format(**fields)
        else:
            ret["text"] = " ".join([str(getattr(instance, field))
                                    for field in self.Meta.field_text])
        return ret

    def get_field_names(self, declared_fields, info):
        """
        Sets the fields and read only fields in the meta class before passing to the
        parrent method.
        """

        if ((hasattr(self.Meta,'fields') and self.Meta.fields is None) 
            or not hasattr(self.Meta,'fields')):
            assert hasattr(self.Meta,'field_id')
            assert hasattr(self.Meta,'field_text')
            text = getattr(self.Meta,'field_text')
            if not isinstance(text,list):
                text = [text]
            self.Meta.fields = [self.Meta.field_id] + text
            self.Meta.read_only_fields = self.Meta.fields

        return super().get_field_names(declared_fields, info)