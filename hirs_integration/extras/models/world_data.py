# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.db import models

def get_country(country_code):
    """
    Returns the country object for the given country code.
    """
    return Country.objects.get(code=country_code)

class Country(models.Model):
    """Countries of the world"""

    data_targets = [
        ('name', 'name', str),
        ('iso2', 'code', str),
        ('iso3', 'iso3', str),
    ]

    class Meta:
        db_table = 'countries'

    id = models.AutoField(primary_key=True)
    #: str: Country name
    name = models.CharField(max_length=255)
    #: str: Country code (ISO 3166-1 alpha-2)
    code = models.CharField(max_length=2)
    #: str: Country code (ISO 3166-1 alpha-3)
    iso3 = models.CharField(max_length=3)


class State(models.Model):
    """Country States"""

    data_targets = [
        ('name', 'name', str),
        ('state_code', 'code', str),
        ('country_code', 'country', get_country),
        ('type', 'type', str),        
    ]

    class Meta:
        db_table = 'states'

    id = models.AutoField(primary_key=True)
    #: str: State name
    name = models.CharField(max_length=255)
    #: str: State code
    code = models.CharField(max_length=255)
    #: Countries: Country this state resides in
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    #: str: State type
    type = models.CharField(max_length=255)