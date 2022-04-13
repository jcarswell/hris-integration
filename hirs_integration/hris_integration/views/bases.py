# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.contrib.auth.decorators import login_required
from django.views.generic.base import View, ContextMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.views import redirect_to_login


class LoggedInView(ContextMixin, View):
    page_title = 'HRIS Sync'
    site_title = 'HRIS Sync'
    page_description = None
    redirect_path = None

    def get_context(self, **kwargs):
        base_context = self.get_context_data(**kwargs)
        context = {
            "site": {
                "name": self.site_title
            },
            "page": {
                "title": self.page_title,
                "description": self.page_description
            }
        }
        base_context.update(**context)
        return base_context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if self.redirect_path == None:
            self.redirect_path = request.path

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(next=self.redirect_path)
        return super().dispatch(request, *args, **kwargs)