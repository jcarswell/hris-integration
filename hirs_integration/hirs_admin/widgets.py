from django.forms.widgets import Widget


class Item(Widget):
    template_name = 'hirs_admin/widgets/item.html'
    
    def render(self, name, value, title, **kwargs):
        context = self.get_context(name,value,title)
        return self._render(self.template_name,context)
    
    def get_context(self, name, value, title) -> dict:
        context = super().get_context(name, value, [])
        context["widget"]["title"] = title
        return context


class Hidden(Widget):
    template_name = 'hirs_admin/widget/hidden.html'