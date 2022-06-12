.. _models_extras_country_data:

Country Data Models
====================

The country and state models are populated based on dr5hn's countries-states-cities database.

.. _[GitHub] dr5hn/countries-states-cities-database: https://github.com/dr5hn/countries-states-cities-database

Country
-------

.. autoclass:: extras.models.Country
   :members:
   :undoc-members: data_targets

:data_targets:
    This represents the data targets to use when importing the csv database and the method
    to use when parsing the data.

    each row is stored in a tuple with the following format:
    (``csv column name``, ``model field name``, ``method to use when parsing the data``)


    :type: list

State
-----

.. autoclass:: extras.models.State
   :members:
   :undoc-members: data_targets

:data_targets:
    This represents the data targets to use when importing the csv database and the method
    to use when parsing the data.

    each row is stored in a tuple with the following format:
    (``csv column name``, ``model field name``, ``method to use when parsing the data``)


    :type: list
