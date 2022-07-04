# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.core.exceptions import ValidationError

__all__ = ("import_validator",)


def import_validator(value) -> None:
    import importlib

    try:
        lib = importlib.import_module(value)
        if not hasattr(lib, "form"):
            raise ValueError
    except ModuleNotFoundError:
        raise ValidationError(f"{value} does not exist", params={"value": value})
    except ValueError:
        raise ValidationError(
            f"{value} is missing the 'form' method", params={"value": value}
        )
