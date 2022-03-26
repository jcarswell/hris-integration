# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import json
import importlib
import os
import sys

from pathlib import Path,PureWindowsPath,PurePosixPath
from django.core.management import utils
from cryptography.fernet import Fernet
from copy import deepcopy
from django.core.exceptions import ImproperlyConfigured

BASE_PATH = Path(__file__).resolve().parent.parent
DATABASE_CHOICES = ['mssql','postgres','mysql']

DB_MSSQL = {
    'ENGINE': 'mssql',
    'HOST': '',
    'NAME': '',
    'OPTIONS': {
        'driver': "SQL Server Native Client 11.0"
    }
}

DB_PG = {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': '',
    'NAME': '',
    'USERNAME': '',
    'PASSWORD': '',
    'PORT': '5432',
}

DB_MYSQL = {
    'ENGINE': 'django.db.backends.mysql',
    'HOST': '',
    'NAME': '',
    'USERNAME': '',
    'PASSWORD': '',
    'PORT': '3306',
}

DEFAULTS = {
    'ALLOWED_HOSTS': ['www.example.com'],
    'TIME_ZONE': 'UTC',
    'STATIC_ROOT': 'static',
    'STATIC_URL': '/static/',
    'DATABASE': DB_MSSQL,
    'MEDIA_ROOT': 'media',
    'MEDIA_URL': '/media/',
    'SECRET_KEY': None,
    'ENCRYPTION_KEY': None,
    'ADDITIONAL_APPS': ['corepoint_export'],
    'PASSWORD_LENGTH': 12,
    'PASSWORD_CHARS': 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789',    
    }

DATABASE_CHOICE_MAP = {
    'mssql': DB_MSSQL,
    'postgres': DB_PG,
    'mysql': DB_MYSQL
}

def config(path:Path,name:str ="config.py",**kwargs) -> bool:
    """Build the configuration file that will be source by the main
    settings module to allow for user configuration that remains separate
    from the core configuration and repo.

    :param path: The path the configuration file will be written to.
    :type path: Path
    :param name: while not advisable to use, allows for the changing of the config file name,
        defaults to "config.py"
    :type name: str, optional
    :return: True if all paths and configuration values are valid and the app can be imported.
        Otherwise, False indicating that the app cannot be imported.
    :rtype: bool
    """

    ret:bool = True

    if Path(path,name).exists(): # Don't override existing config
        print(f"{Path(path,name)} already exists, skipping.")
        return True

    for key in DEFAULTS.keys(): #Loop through the kwargs and update the defaults
        if key in kwargs.keys():
            DEFAULTS[key] = kwargs[key]

    try:
        check_legacy_config()
    except ImproperlyConfigured:
        pass

    for key in DEFAULTS.keys(): #Check the configuration values
        if key[-5:] == '_ROOT': 
            # Make sure that all _ROOT paths are valid otherwise convert them into
            # local paths that are valid.
            lp = Path(BASE_PATH,DEFAULTS[key].lstrip('/').lstrip('\\')) # strip leading slashes
            if not Path(DEFAULTS[key]).exists() or not lp.exists():
                print(f"Creating '{str(lp)}'")
                lp.mkdir()
                DEFAULTS[key] = lp
            elif lp.exists():
                DEFAULTS[key] = lp
            else:
                print(f"The path for '{key}' {DEFAULTS[key]} is not valid, please correct it in {name}"
                      "before continuing.")
                ret = False

        if key[-4:] == '_URL': # Django requires the trailing slash
            if DEFAULTS[key][-1] != '/':
                DEFAULTS[key] += '/'

    if DEFAULTS['SECRET_KEY'] is None:
        DEFAULTS['SECRET_KEY'] = utils.get_random_secret_key()

    if DEFAULTS['ENCRYPTION_KEY'] is None:
        DEFAULTS['ENCRYPTION_KEY'] = Fernet.generate_key().decode('utf-8')

    with open(Path(path,name),'w') as conf:
        for k,v in DEFAULTS.items():
            if type(v) == str:
                conf.write(f"{k} = '{esc_str(v)}'\n")
            elif type(v) == dict:
                conf.write(f"{k} = {json.dumps(v,indent=2,)}\n")
            elif isinstance(v,(PureWindowsPath,PurePosixPath,Path)):
                conf.write("{} = '{}'\n".format(k,esc_str(str(v))))
            else:
                conf.write(f"{k} = {v}\n")

    for key in ['NAME','ENGINE','HOST']: # Not a comprehensive database config check
        if key not in DEFAULTS['DATABASE'].keys():
            ret = False

    return ret

def esc_str(str) -> str:
    """Escape single quotes in a string.

    :param str: The string to escape.
    :type str: str
    :return: The escaped string.
    :rtype: str
    """
    return str.replace('\\','\\\\')

def check_legacy_config():
    """Check for any legacy configuration in the settings module and update the configuration.
    """
    try:
        settings = importlib.import_module(os.environ.get('DJANGO_SETTINGS_MODULE',
                                                          'hris_integration.settings'))
    except ModuleNotFoundError:
        return

    if hasattr(settings,'VERSION'):
        # The settings module has already been updated, so we don't wan't to pull the vars from it.
        return
    
    for key in DEFAULTS.keys():
        if hasattr(settings,key) and getattr(settings,key) and key != 'DATABASES':
            DEFAULTS[key] = getattr(settings,key)

    if hasattr(settings,'DATABASES') and settings.DATABASES['default']['NAME']:
        print("Copying database settings from settings.py")
        DEFAULTS['DATABASE'] = deepcopy(settings.DATABASES['default'])

    print("Settings have been copied from settings.py, please review your config.py to ensure "
          "everything is correct.")
