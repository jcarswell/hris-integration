# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from django.forms import forms
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict
from django.template import loader
from django.forms.fields import Field

from hirs_admin.fields import SettingFieldGenerator
from hirs_admin.helpers.config import setting_parse
from hirs_admin.exceptions import RenderError

logger = logging.getLogger('hirs_admin.settings_view')

class Form(forms.Form):
    def __init__(self,**kwargs):
        self.base_fields = {
            key: kwargs.pop(key) for key, value in list(kwargs.items())
            if isinstance(value, Field)
        }
        self.declared_fields = self.base_fields
        super().__init__(**kwargs)

    def as_form(self):
        output = []
        hidden_fields = []

        for name,_ in self.fields.items():
            classes = ["form-control"]
            bf = self[name]
            if bf.is_hidden:
                hidden_fields.append(bf.as_hidden)
            else:
                if bf.label:
                    label = bf.label_tag() or ''
                output.append('<div>')
                output.append(label)
                output.append(f'<span class="text-secondary">{bf.help_text}</span>')
                output.append(bf.as_widget(attrs={'class':" ".join(classes)}))
                output.append('</div>')

        if hidden_fields:
            output.append(hidden_fields)

        return mark_safe('\n'.join(output))

    def __str__(self) -> str:
        return self.as_form()

class Settings():
    def __init__(self,objects):
        self.items = {}
        self.fields = {}
        self.update_groups(objects)
        self.generate_sub_form()

    def update_groups(self,objects):
        output = {}
        for row in objects:
            group = row.group
            if group not in output:
                output[group] = {
                    "_NAME_": row.group_text,
                }
                logger.debug(f"Added Catagory: {group}")

            output[group].update(self.update_catagories(output[group], row))

            self.items = dict(sorted(output.items()))

    def update_catagories(self, data, row):
        if row.catagory not in data:
            data[row.catagory] = {
                "_NAME_": row.catagory_text,
            }
            logger.debug(f"Added group {row.catagory}")

        data[row.catagory].update(self.update_item(data[row.catagory], row))

        return data

    def update_item(self, data, row):
        field,value = SettingFieldGenerator(row)

        data[setting_parse(setting=row)] = field
        self.fields[setting_parse(setting=row)] = value

        return data

    def as_nav(self):
        output = []
        for gname,group in self.items.items():
            output.append(
                f'<a class="list-group-item list-group-item-action" href="#{gname}">{ group["_NAME_"] }</a>'
            )
            output.append('<nav class="nav nav-pills flex-column">')
            for cname,cat in group.items():
                if cname[0]+cname[-1] != "__":
                    output.append(
                        f'<a class="nav-link ml-3 my-1" href="#{gname}_{cname}">{cat["_NAME_"]}</a>'
                    )
            output.append('</nav>')
        
        return mark_safe('\n'.join(output))
    
    def as_html(self):
        output = []
        for group,catagories in self.items.items():
            output.append(f'<h3 id="{group}">{catagories["_NAME_"]}</h3>')
            output.append('<hr style="border-top:2px solid #bbb">')
            for catagory in catagories:
                if catagory[0]+catagory[-1] != "__":
                    try:
                        t = loader.get_template('hirs_admin/components/form.html')
                    except loader.TemplateDoesNotExist as e:
                        raise RenderError("Unable to load form template",e)
                    c = {
                        "form_id": f"{group}_{catagory}",
                        "title": catagories[catagory]["_NAME_"],
                        "form": catagories[catagory]["_FORM_"],
                    }

                    output.append(t.render(c))

        return mark_safe('\n'.join(output))
    
    def __str__(self) -> str:
        self.as_html()

    def generate_sub_form(self):
        for group,catagories in self.items.items():
            for cname,cat in catagories.items():
                form_fields = {}
                values = MultiValueDict()
                if cname[0]+cname[-1] != "__":
                    for id,item in cat.items():
                        if id != "_NAME_":
                            form_fields[id] = item
                            values[id] = self.fields[id].value

                    self.items[group][cname]["_FORM_"] = Form(data=values,
                                                              field_order=sorted(form_fields.keys()),
                                                              **form_fields)