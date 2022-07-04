# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.forms import forms
from django.forms.fields import Field
from django.utils.safestring import mark_safe


class Form(forms.Form):
    def __init__(self, **kwargs):
        self.base_fields = {
            key: kwargs.pop(key)
            for key, value in list(kwargs.items())
            if isinstance(value, Field)
        }
        self.declared_fields = self.base_fields
        super().__init__(**kwargs)

    def as_form(self):
        output = []
        hidden_fields = []

        for name, _ in self.fields.items():
            classes = ["form-control"]
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                if bf.label:
                    label = bf.label_tag() or ""
                output.append("<div>")
                output.append(label)
                output.append(f'<span class="text-secondary">{bf.help_text}</span>')
                output.append(bf.as_widget(attrs={"class": " ".join(classes)}))
                output.append("</div>")

        if hidden_fields:
            output.append(hidden_fields)

        return mark_safe("\n".join(output))

    def __str__(self) -> str:
        return self.as_form()
