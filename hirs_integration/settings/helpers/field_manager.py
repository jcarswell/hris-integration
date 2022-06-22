# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any
from distutils.util import strtobool
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import make_aware


class FieldConversion:
    """
    Converts a field value from it stored string state to it's proper type based on the
    provided type. The value is stored in the returned object as value, and support
    the reverse functions required to save the field as a string

    Usage:
        f = FieldConversion(type:AnyStr)
        f(value) -> value
        f.value = 123
        str(f)

    :raises TypeError: Unsupported type provided
    """

    def __init__(self, type: str, value: str = None) -> None:
        try:
            self.field = eval(f"self.{type}")
            self.type = type
        except NameError:
            raise TypeError("Unsupported Type provided")
        if value:
            self.field(value)

    def __eq__(self, value) -> bool:
        if isinstance(value, FieldConversion):
            return (
                self.value == value.value
                and self.type == value.type
                and self.field == value.field
            )
        elif isinstance(value, str):
            v = FieldConversion(self.type, value)
            return self.value == v.value

        return False

    def __call__(self, value: str) -> Any:
        self.field(value)

    def CharField(self, value) -> str:
        self.value = value

    def RegexField(self, value):
        self.CharField(value)

    def BooleanField(self, value):
        self.value = strtobool(value)

    def ChoiceField(self, value):
        self.CharField(value)

    def MultipleChoiceField(self, value):
        self.value = value.split(",")

    def IntegerField(self, value):
        self.value = int(value)

    def FloatField(self, value):
        self.value = float(value)

    def DecimalField(self, value):
        self.FloatField(value)

    def DateField(self, value):
        self.value = parse_date(value)

    def DateTimeField(self, value):
        self.value = parse_datetime(value)
        try:
            self.value = make_aware(self.value)
        except ValueError:
            # self.value is already tz enabled
            pass

    def Pattern(self):
        return str(self.value.pattern)

    def list(self):
        return ",".join(self.value)

    def __str__(self) -> str:
        if not hasattr(self, "value"):
            return ""
        try:
            return eval(f"self.{self.value.__class__.__name__}")()
        except NameError:
            return str(self.value)
        except AttributeError:
            return str(self.value)
