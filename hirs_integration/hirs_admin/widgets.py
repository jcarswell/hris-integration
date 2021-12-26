from django.forms.widgets import Select, Widget

class Item(Widget):
    template_name = 'hirs_admin/widgets/item.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["title"] = self.title
        return context


class Hidden(Item):
    template_name = 'hirs_admin/widgets/hidden.html'


class SelectPicker(Select):
    template_name = 'hirs_admin/widgets/selectpicker.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["title"] = self.title
        return context

class SelectPickerMulti(SelectPicker):
    template_name = 'hirs_admin/widgets/selectpicker-multi.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["max_opts"] = self.max_opts or 0