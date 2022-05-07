# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from django.views.generic.base import TemplateResponseMixin
from hris_integration.views import LoggedInView

from .helpers import settings_view,config

logger = logging.getLogger('hirs_admin.view')

class Index(TemplateResponseMixin, LoggedInView):
    """Home Page"""
    template_name = 'base/base.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context(**kwargs)
        return self.render_to_response(context)


class JobActions(TemplateResponseMixin, LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Job Actions'
    template_name = 'actions.html'

    def get(self, request, *args, job:str =None, **kwargs):
        return self.render_to_response(self.get_context(**kwargs))

    def post(self, request, *args, job:str =None, **kwargs):
        pass