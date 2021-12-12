import importlib

from django.core.exceptions import ValidationError

__all__ = ('import_validator','import_field_choices')

def import_validator(value) -> None:
    try:
        lib = importlib.import_module(value)
        if not hasattr(lib,'form'):
            raise ValueError
    except ModuleNotFoundError:
        raise ValidationError(f"{value} does not exist",
                              params={'value': value})
    except ValueError:
        raise ValidationError(f"{value} is missing the 'form' method",
                              params={'value': value})
        
def import_field_choices():
    from ftp_import.helpers.config import get_fields
    fields = get_fields()
    for field in fields.keys():
        yield((field,field))