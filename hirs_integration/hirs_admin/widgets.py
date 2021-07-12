from django.forms.widgets import Widget


class Item(Widget):
    template_name = 'hirs_admin/widgets/item.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["title"] = self.title
        return context        

class Hidden(Item):
    template_name = 'hirs_admin/widgets/hidden.html'