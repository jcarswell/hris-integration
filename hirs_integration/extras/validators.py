# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.validators import ValidationError
from django.utils.translation import gettext_lazy as _t

from common.functions import model_to_choices

__all__ = ('email_template_list',)

def countries_list(none:bool =True):
    """Returns a Choice iterator for the available countries

    :param none: Include the None or unset option, defaults to True
    :type none: bool, optional
    :return: Django choice objects
    :rtype: iterable
    """

    from extras.models import Countries
    return model_to_choices(Countries.objects.all(), none=none)

def states_list(country:str =None, none:bool =True):
    """Returns a Choice iterator for the available states filtered by country

    :param country: The country to filter by, defaults to None
    :param none: Include the None or unset option, defaults to True
    :type none: bool, optional
    :return: Django choice objects
    :rtype: iterable
    """

    from extras.models import Countries, States
    if isinstance(country, Countries):
        return model_to_choices(States.objects.filter(country=country), none=none)
    elif isinstance(country, str):
        if len(country) == 2:
            try:
                country = Countries.objects.get(code=country)
            except Countries.DoesNotExist:
                try:
                    country = Countries.objects.filter(name=country)
                except Countries.DoesNotExist:
                    raise ValidationError(_t('Invalid country code or name.'))
        elif len(country) == 3:
            try:
                country = Countries.objects.get(iso3=country)
            except Countries.DoesNotExist:
                try:
                    country = Countries.objects.filter(name=country)
                except Countries.DoesNotExist:
                    raise ValidationError(_t('Invalid country code or name.'))
        else:    
            try:
                country = Countries.objects.filter(name=country)
            except Countries.DoesNotExist:
                raise ValidationError(_t('Invalid country code or name.'))

        return model_to_choices(States.objects.filter(country=country), none=none)
    else:
        return model_to_choices(Countries.objects.all(), none=none)