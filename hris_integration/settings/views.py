# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin
from hris_integration.views import LoggedInView
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict
from django.template import loader

from .validators import ValidationError, setting_parse
from . import models
from .fields import SettingFieldGenerator
from .forms.settings_base import Form
from .exceptions import RenderError

logger = logging.getLogger("settings.view")


class SettingSubView:
    def __init__(self, objects):
        self.items = {}
        self.fields = {}
        self.update_groups(objects)
        self.generate_sub_form()

    def update_groups(self, objects):
        output = {}
        for row in objects:
            group = row.group
            if group not in output:
                output[group] = {
                    "_NAME_": row.group_text,
                }
                logger.debug(f"Added Category: {group}")

            output[group].update(self.update_catagories(output[group], row))

            self.items = dict(sorted(output.items()))

    def update_catagories(self, data, row):
        if row.category not in data:
            data[row.category] = {
                "_NAME_": row.category_text,
            }
            logger.debug(f"Added group {row.category}")

        data[row.category].update(self.update_item(data[row.category], row))

        return data

    def update_item(self, data, row):
        field, value = SettingFieldGenerator(row)

        data[setting_parse(setting=row)] = field
        self.fields[setting_parse(setting=row)] = value

        return data

    def as_nav(self):
        output = []
        for gname, group in self.items.items():
            output.append(
                f'<a class="list-group-item list-group-item-action" href="#{gname}">'
                f'{ group["_NAME_"] }</a>'
            )
            output.append('<nav class="nav nav-pills flex-column">')
            for cname, cat in group.items():
                if cname[0] + cname[-1] != "__":
                    output.append(
                        f'<a class="nav-link ml-3 my-1" href="#{gname}_{cname}">'
                        f'{cat["_NAME_"]}</a>'
                    )
            output.append("</nav>")

        return mark_safe("\n".join(output))

    def as_html(self):
        output = []
        for group, catagories in self.items.items():
            output.append(f'<h3 id="{group}">{catagories["_NAME_"]}</h3>')
            output.append('<hr style="border-top:2px solid #bbb">')
            for category in catagories:
                if category[0] + category[-1] != "__":
                    try:
                        t = loader.get_template("components/form.html")
                    except loader.TemplateDoesNotExist as e:
                        raise RenderError("Unable to load form template", e)
                    c = {
                        "form_id": f"{group}_{category}",
                        "title": catagories[category]["_NAME_"],
                        "form": catagories[category]["_FORM_"],
                    }

                    output.append(t.render(c))

        return mark_safe("\n".join(output))

    def __str__(self) -> str:
        self.as_html()

    def generate_sub_form(self):
        for group, catagories in self.items.items():
            for cname, cat in catagories.items():
                form_fields = {}
                values = MultiValueDict()
                if cname[0] + cname[-1] != "__":
                    for id, item in cat.items():
                        if id != "_NAME_":
                            form_fields[id] = item
                            values[id] = self.fields[id].value

                    self.items[group][cname]["_FORM_"] = Form(
                        data=values,
                        field_order=sorted(form_fields.keys()),
                        **form_fields,
                    )


class Settings(TemplateResponseMixin, LoggedInView):
    """User Configurable Settings"""

    http_method_names = ["get", "post", "head", "options", "trace"]
    page_title = "Settings"
    template_name = "settings/settings.html"

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        settings_data = SettingSubView(models.Setting.o2.all())

        context = self.get_context(**kwargs)
        context["settings"] = settings_data

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        logger.debug(f"got post with data: {request.POST}")
        errors = {}
        for html_id, val in request.POST.items():
            if html_id != "":
                try:
                    setting = setting_parse(html_id=html_id)
                    base_field, base_value = SettingFieldGenerator(setting)
                    logger.debug(f"Checking {html_id}")
                    if base_value.value != str(val):
                        base_field.to_python(val)
                        base_field.run_validators(val)
                        base_value(val)
                        logger.debug(f"Field updated and validated {base_value}")
                        setting.value = str(base_value.value)
                        setting.save()
                except ValueError:
                    logger.debug(f"Item {html_id} is not a valid setting ID")
                    errors[html_id] = None
                except TypeError:
                    logger.debug(f"Caught TypeError setting up field for {html_id}")
                    errors[html_id] = None
                except ValidationError as e:
                    logger.debug(f"Caught validationError - {iter(e)}")
                    if hasattr(e, "error_list"):
                        errors[html_id] = e

        if errors == {}:
            return JsonResponse({"status": "success"})
        else:
            ers = []
            for e in errors.values():
                ers.append("<br>".join(e))
            return JsonResponse(
                {"status": "error", "fields": list(errors.keys()), "errors": ers}
            )

    def put(self, request, *args, **kwargs):
        self.post(self, request, *args, **kwargs)
