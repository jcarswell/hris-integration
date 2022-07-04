# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.db.utils import ProgrammingError
from warnings import warn
from django.conf import settings
from random import choice

def pk_to_name(pk:int) -> str:
    if not isinstance(pk,int):
        raise TypeError(f"Expected int got \"{pk.__class__.__name__}\"")

    return f"id_{pk}"

def name_to_pk(name:str) -> int:
    if isinstance(name,int):
        return name
    elif isinstance(name,str):
        return int(name.replace("id_",""))
    else:
        raise TypeError(f"Expected str got \"{name.__class__.__name__}\"")

def model_to_choices(data,none:bool =False):
    output = []
    if none:
        output.append((None,""))
    try:
        for r in data:
            output.append((pk_to_name(r.pk),str(r)))
    except (ProgrammingError,AttributeError):
            warn("Databases not initialized")
            output = [('Not Loaded','System not initalized')]
    return output

def password_generator(length:int = None, chars:str = None) -> str:
    """A simple password generator. If no length or chars are provided, the default
    is used from the configuration.

    REF: 
    - config.PASSWORD_LENGTH
    - config.PASSWORD_CHARS
    
    :param length: The length of the password to generate
    :type length: int, optional
    :param chars: The characters to use when generating the password
    :type chars: str, optional
    :return: A password of the specified length
    :rtype: str
    """

    if not length:
        length = settings.PASSWORD_LENGTH
    if not chars:
        chars = settings.PASSWORD_CHARS
    return ''.join(choice(chars) for _ in range(length))

def get_model_pk_name(model) -> str:
    """Gets the model primary key field name

    :param model: the model to get the primary key field name from
    :type model: django.models.Model
    :return: the field name of the primary key
    :rtype: str
    """

    for f in model._meta.fields:
        if f.primary_key:
            return f.name