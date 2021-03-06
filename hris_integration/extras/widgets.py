# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from django.forms import widgets

logger = logging.getLogger("Widgets")


class WidgetClassBase:
    base_classes = None

    def update_classes(self, attrs: dict = None) -> str:
        if (
            attrs == None
            or ("class" not in attrs)
            or ("class" in attrs)
            and attrs["class"] == ""
        ):
            classes = self.base_classes or []
        elif "class" in attrs:
            classes = attrs["class"].split(" ")
            for cls in self.base_classes:
                if cls not in classes:
                    classes.append(cls)

        return " ".join(classes)


class Hidden(widgets.Input):
    template_name = "widgets/hidden.html"
    input_type = "password"

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs["data-toggle"] = "password"


class SelectPicker(widgets.Select, WidgetClassBase):
    template_name = "widgets/selectpicker.html"
    base_classes = ["selectpicker"]

    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)
        self.attrs["data-live-search"] = "true"
        self.attrs["data-style"] = "bg-white"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"]["class"] = self.update_classes(attrs)
        return context


class SelectPickerMulti(widgets.SelectMultiple, WidgetClassBase):
    template_name = "widgets/selectpicker.html"
    base_classes = ["selectpicker"]

    def __init__(self, attrs=None, choices=(), max_opts=None, select_box=True):
        super().__init__(attrs, choices)
        self.attrs["data-live-search"] = "true"
        self.attrs["data-style"] = "bg-white"
        self.attrs["max_opts"] = max_opts or 0
        self.attrs["data-actions-box"] = str(select_box).lower()

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"]["class"] = self.update_classes(attrs)
        return context


class CheckboxInput(widgets.CheckboxInput, WidgetClassBase):
    base_classes = ["input-md"]

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"]["class"] = self.update_classes(attrs)
        return context
