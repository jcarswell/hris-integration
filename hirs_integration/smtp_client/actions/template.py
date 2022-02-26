import logging

from hris_integration.data_structures import EmployeeMangaer
from jinja2 import Environment,PackageLoader

from smtp_client.smtp import Smtp
from smtp_client.exceptions import SmtpServerError,SmtpToInvalid