from django.core.exceptions import ValidationError

__all__ = ('import_validator',)

def import_validator(value) -> None:
    import importlib
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