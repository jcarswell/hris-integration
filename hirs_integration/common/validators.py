# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

"""
This is the core validator module that ensure all validators from installed apps are 
available as needed for any validators or choices to be used.
"""

import importlib
import logging

from warnings import warn
from hris_integration.settings import INSTALLED_APPS

logger = logging.getLogger('common.validators')

## Dynamically import all validators from installed apps
__ALL_APPS__ = []
for app in INSTALLED_APPS:
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