# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from jinja2 import Environment,select_autoescape

from smtp_client.smtp import Smtp
from smtp_client.exceptions import InvlaidTemplate
from smtp_client.models import EmailTemplates

logger = logging.getLogger('smtp_client.SmtpTemplate')
class SmtpTemplate:
    def __init__(self,template:str =None,subject:str =None,body:str =None,to:str =None,**kwargs):
        if to is None:
            raise ValueError("the 'to' argument is required")

        if template:
            try:
                template_obj:EmailTemplates = EmailTemplates.objects.get(template_name=template)
                subject = template_obj.email_subject
                body = template_obj.email_body
            except EmailTemplates.DoesNotExist as e:
                logger.critical(f"The template '{template}' is no longer valid, please check "
                                "the configuration")
                raise InvlaidTemplate(e,template_name=template)

        if subject is None and body is None:
            raise ValueError("If the template name is not provided then the subject and body "
                             "fields are required")

        env = Environment(
            autoescape=select_autoescape()
        )
        self.env_subject = env.from_string(subject)
        self.env_body = env.from_string(body)
        self.to = to
        self.kwargs = kwargs

    def make_context(self,**kwargs) -> dict:
        context = self.kwargs
        context.update(kwargs)
        return context

    def send(self,**kwargs) -> None:
        context = self.make_context(**kwargs)
        s = Smtp()
        msg = s.mime_build(html=self.env_body.render(context),
                           subject=self.env_subject.render(context),
                           to=self.to)
        s.send_html(self.to,msg)