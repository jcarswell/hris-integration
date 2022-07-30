# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db.utils import ProgrammingError
from warnings import warn
from django.conf import settings
from random import choice
from typing import List, Tuple


def pk_to_name(pk: int) -> str:
    """
    Convert a primary key to a string name used for Django html forms. This is not used
    for API's which use the primary key as the primary key.

    :param pk: the primary key to convert
    :type pk: int
    :raises TypeError: if the primary key is not an integer
    :return: django form formatted field name
    :rtype: str
    """
    if not isinstance(pk, int):
        raise TypeError(f'Expected int got "{pk.__class__.__name__}"')

    return f"id_{pk}"


def name_to_pk(name: str) -> int:
    """
    Converts a Django form field name to a primary key. Note if the name is not a valid
    primary key field name, a ValueError will be raised when converting the string to a
    integer.

    :param name: The string name of the field
    :type name: str
    :raises TypeError: If the name is not a string or integer
    :return: The primary key extracted from the name
    :rtype: int
    """
    if isinstance(name, int):
        return name
    elif isinstance(name, str):
        return int(name.replace("id_", ""))
    else:
        raise TypeError(f'Expected str got "{name.__class__.__name__}"')


def model_to_choices(
    data: "django.db.model.queryset", none: bool = False
) -> List[Tuple[str, object]]:
    """
    Converts a model queryset to a list of choices.

    :param data: The queryset
    :type data: django.db.model.queryset
    :param none: Include any empty value at the start, defaults to False
    :type none: bool, optional
    :return: a Django choice list
    :rtype: List[Tuple(str, object)]
    """

    output = []
    if none:
        output.append((None, ""))
    try:
        for r in data:
            output.append((pk_to_name(r.pk), str(r)))
    except (ProgrammingError, AttributeError):
        warn("Databases not initialized")
        output = [("Not Loaded", "System not initialized")]

    return output


def password_generator(length: int = None, chars: str = None) -> str:
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
    return "".join(choice(chars) for _ in range(length))


def get_model_pk_name(model: "django.models.Model") -> str:
    """Gets the model primary key field name

    :param model: the model to get the primary key field name from
    :type model: django.models.Model
    :return: the field name of the primary key
    :rtype: str
    """

    for f in model._meta.fields:
        if f.primary_key:
            return f.name


class PhoneNumber:
    """
    A phone number helper to ensure that number are properly formatted and provides
    a method for pretty print.

    Available methods:
    - __str__: Returns the phone number as a string
    - eq, lt, gt: Compare the phone number to another phone number

    Available attributes:
    - number: The phone number as a string
    - pretty: Returns the phone number as a string with a pretty format
    """

    def __init__(self, number=str) -> None:
        if isinstance(number, int):
            self.number = str(number)
        elif isinstance(number, str):
            parse = []
            for i in number:
                if i.isdigit():
                    parse.append(i)
            self.number = "".join(number)
        else:
            raise ValueError(f"Expected a string got {number.__class__.__name__}")

    def __str__(self) -> str:
        return self.number

    def __repr__(self) -> str:
        return self.number

    @property
    def pretty(self) -> str:
        return "%s%s%s-%s%s%s-%s%s%s%s" % tuple(self.number)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, PhoneNumber):
            return self.number == o.number
        else:
            return False

    def __gt__(self, o: object) -> bool:
        if isinstance(o, int):
            return int(self.number) < o
        elif isinstance(o, str):
            o = PhoneNumber(o)
        if isinstance(o, PhoneNumber):
            return int(self.number) < int(o.number)
        else:
            return False

    def __lt__(self, o: object) -> bool:
        if isinstance(o, int):
            return int(self.number) > o
        elif isinstance(o, str):
            o = PhoneNumber(o)
        if isinstance(o, PhoneNumber):
            return int(self.number) > int(o.number)
        else:
            return False
