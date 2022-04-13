# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin
from django.core.exceptions import ValidationError
from hris_integration.views import LoggedInView

from .helpers import settings_view,config
from .fields import SettingFieldGenerator
from . import models

logger = logging.getLogger('hirs_admin.view')


class Index(TemplateResponseMixin, LoggedInView):
    """Home Page"""
    template_name = 'hirs_admin/base.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context(**kwargs)
        return self.render_to_response(context)


class Settings(TemplateResponseMixin, LoggedInView):
    """User Configurable Settings"""
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Settings'
    template_name = 'hirs_admin/settings.html'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        settings_data = settings_view.Settings(models.Setting.o2.all())
        
        context = self.get_context(**kwargs)
        context["settings"] = settings_data

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        logger.debug(f"got post with data: {request.POST}")
        errors = {}
        for html_id,val in request.POST.items():
            if html_id != '':
                try:
                    setting = config.setting_parse(html_id=html_id)
                    base_field,base_value = SettingFieldGenerator(setting)
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
                    if hasattr(e,'error_list'):
                        errors[html_id] = e

        if errors == {}:
           return JsonResponse({"status":"success"})
        else:
            ers = []
            for e in errors.values():
                ers.append("<br>".join(e))
            return JsonResponse({"status":"error",
                                 "fields":list(errors.keys()),
                                 "errors":ers})

    def put(self, request, *args, **kwargs):
        self.post(self, request, *args, **kwargs)


class JobActions(TemplateResponseMixin, LoggedInView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    page_title = 'Job Actions'
    template_name = 'hirs_admin/actions.html'

    def get(self, request, *args, job:str =None, **kwargs):
        return self.render_to_response(self.get_context(**kwargs))

    def post(self, request, *args, job:str =None, **kwargs):
        pass