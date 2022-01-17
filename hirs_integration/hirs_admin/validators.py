import importlib
import logging
import re

from warnings import warn
from hris_integration.settings import INSTALLED_APPS
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _t

logger = logging.getLogger('hris_admin.validators')

## Dynamically import all validators from installed apps
__ALL_APPS__ = []
for app in INSTALLED_APPS + ['common']:
    if app[:10] != 'hirs_admin':
        try:
            module = importlib.import_module(app + ".validators")
            if hasattr(module,'__all__'):
                __ALL_APPS__.append(module)
                for validator in module.__all__:
                    logger.debug(f"Trying to add {module.__name__}.{validator} to global name space")
                    if validator not in globals():
                        try:
                            globals()[validator] = eval(f"module.{validator}")
                        except AttributeError:
                            logger.warn(f"Failed to import {validator}")
                    else:
                        warn(f"{validator} from {module} is duplicated ")
            else:
                logger.debug(f"{module.__name__} exists but is missing an __all__ attribute")
        except ModuleNotFoundError:
            logger.debug(f'App {app} has no validators module')

class DnValidator(RegexValidator):
    regex = r'^((CN=([^,]*)),)?((((?:CN|OU)=[^,]+,?)+),)?((DC=[^,]+,?)+)$',
    message=_t("Not a valid DN string")
    flags=re.IGNORECASE