import logging

from django.forms import widgets

logger = logging.getLogger("Widgets")

class Hidden(widgets.Input):
    template_name = 'hirs_admin/widgets/hidden.html'
    input_type = 'password'
    
    def __init__(self,attrs=None):
        super().__init__(attrs)
        self.attrs["data-toggle"] = "password"


class SelectPicker(widgets.Select):
    template_name = 'hirs_admin/widgets/selectpicker.html'

    def __init__(self,attrs):
        super().__init__(attrs)
        self.attrs['data-live-search'] = 'true'
        self.attrs['data-style'] = 'bg-white'

    def get_context(self, name, value, attrs):
        context = super().get_context(name,value,attrs)

        if 'class' not in attrs:
            context['widget']['attrs']['class'] = "selectpicker"
        else:
            context['widget']['attrs']['class'] = " ".join(attrs['class'].split(' ') + ['selectpicker'])

        return context


class SelectPickerMulti(widgets.SelectMultiple):
    template_name = 'hirs_admin/widgets/selectpicker-multi.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["max_opts"] = self.max_opts or 0


class CheckboxInput(widgets.CheckboxInput):
    def get_context(self, name, value, attrs):
        context = super().get_context(name,value,attrs)

        logger.debug(f"{name} - {attrs}")
        if 'class' in attrs:
            classes = attrs['class'].split(' ')
            add_class = True
            for x in classes:
                if x[:5] == "input":
                    add_class = False
            if add_class:
                classes.append('input-md')
                context['widget']['attrs']['class'] = " ".join(classes)
            logger.debug(f"{context}")
        else:
            context['widget']['attrs']['class'] = "input-md"

        return context
