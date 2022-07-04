# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List
from django.db import models


def get_country(country_code) -> "Country":
    """
    Returns the country object for the given country code.
    """
    return Country.objects.get(code=country_code)


class Country(models.Model):
    """Countries of the world"""

    data_targets: List[tuple] = [
        ("name", "name", str),
        ("iso2", "code", str),
        ("iso3", "iso3", str),
    ]

    class Meta:
        db_table = "countries"

    id = models.AutoField(primary_key=True)
    #: Country name
    name: str = models.CharField(max_length=255)
    #: Country code (ISO 3166-1 alpha-2)
    code: str = models.CharField(max_length=2)
    #: Country code (ISO 3166-1 alpha-3)
    iso3: str = models.CharField(max_length=3)


class State(models.Model):
    """Country States"""

    data_targets: List[tuple] = [
        ("name", "name", str),
        ("state_code", "code", str),
        ("country_code", "country", get_country),
        ("type", "type", str),
    ]

    class Meta:
        db_table = "states"

    id = models.AutoField(primary_key=True)
    #: State name
    name: str = models.CharField(max_length=255)
    #: State code
    code: str = models.CharField(max_length=255)
    #: Country this state resides in
    country: Country = models.ForeignKey(Country, on_delete=models.CASCADE)
    #: State type
    type: str = models.CharField(max_length=255)
