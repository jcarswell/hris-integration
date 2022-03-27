# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from django.utils.safestring import mark_safe
from django import forms

logger = logging.getLogger('hirs_admin.forms')

class Form(forms.ModelForm):
    """Adds the as_form view and sets that as the default render method.
    
    :param list_fields: Sets the fields to render for as_view, when set to None it will render all fields,
        defaults to None
    :type list_fields: list
    """

    list_fields = None

    def as_form(self) -> None:
        """renders a form using the bootstrap from model.

        This method extends the Meta sub-class and checks for the following additional paramaters
        :params Meta.classes: A list of fields and the classes that should be included as part of the field
        :type Meta.classes: dict
        :param Meta.disabled: A list of fields that should be disable
        :type Meta.disabled: list
        """
        output = []
        hidden_fields = []

        logger.debug(f"Building {self.__class__.__name__} as html form")

        for name in self.fields.keys():
            classes = ["form-control"]
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                attrs={}
                if bf.label:
                    label = bf.label_tag() or ''
                output.append('<div class="form-row">')
                output.append(label)

                if hasattr(self.Meta, 'required') and bf.name in self.Meta.required:
                    attrs['required'] = True

                if hasattr(self.Meta, 'classes') and bf.name in self.Meta.classes:
                    if isinstance(self.Meta.classes[bf.name],str):
                        classes.append(self.Meta.classes[bf.name])
                    elif isinstance(self.Meta.classes[bf.name],(list,tuple)):
                        classes = classes + list(self.Meta.classes[bf.name])
                attrs['class'] = " ".join(classes)

                if hasattr(self.Meta,'disabled') and bf.name in self.Meta.disabled:
                    attrs['disabled'] = True

                output.append(bf.as_widget(attrs=attrs))
                output.append('</div>')

        if hidden_fields:
            output.append(hidden_fields)

        return mark_safe('\n'.join(output))

    def __str__(self) -> str:
        """Returns the as_form method"""
        return self.as_form()