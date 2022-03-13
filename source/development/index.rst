.. _dev:

Deveplopting and Extending the HIRS Integration System
======================================================

.. toctree::
    :glob:
    :maxdepth: 2
    :hidden:
    :caption: Developing and Extending

    extending/*

.. _dev_setup-env:

Setting up a Development Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Set up to virtual environment in the venv folder ``python -m venv venv``
2. Activate your vitual environment
   **Linux**

   .. code-block::

       source venv/bin/activate
    
    **PowerShell**

    .. code-block::

       .\venv\scripts\Activate.ps1

3. Install the required modules

   .. code-block::

      python -m pip install -U -r requirements.txt

4. If you will be updating documentation you will also need to install the dev requirments

    .. code-block::

       python -m pip install -U -r requirements.txt

.. _dev_coding-standards:

Coding Standards
----------------
Coding should follow the PEP8 standards except when referacing AD attributes.
*line lengths should be concidered a suggestion*

^^^^^^^^^^^^^^^^^^^^^^^
Basic module structure 
^^^^^^^^^^^^^^^^^^^^^^^

| your_module/
| ├── __init__.py
| ├── app.py
| ├── exeptions/
| │ ├── __init__.py
| │ └── errors.py
| ├── helpers/
| │ ├── __init__.py
| │ ├── config.py
| │ └── settings_fields.py
| └── validators.py
| 

The following modules are optional and should be defined as needed

| your_module/
| ├── admin.py
| ├── forms.py
| ├── managment/
| │ ├── __init__.py
| │ ├── commands
| │ │ ├── __init__.py
| │ └ └── your-command.py
| ├── model.py
| ├── static/
| │ └── your_module/
| ├── templates/
| │ └── your_module/
| └── views.py
| 
| 

your_module/__init__.py
"""""""""""""""""""""""
Import all non-base exceptions
Import the app config

defined your imports in the __all__ tuple

define setup() - pass is acceptable if you don't have any setup tasks
- Setup is only called during the install, this is a good place to define any scheduled jobs.

your_module/app.py
""""""""""""""""""
Base django app config - your app must be added to the INSTALLED_APPS setting

your_module/excptions/__init__.py
"""""""""""""""""""""""""""""""""
Import all non-base exceptions and warning if you have them

your_module/excptions/errors.py
"""""""""""""""""""""""""""""""
Defines ``YourModuleBaseError``. Optionally extended from ``common.exceptions.HrisIntegrationBaseError``

Define any addtional errors that assist with troubleshooting error or catching specific conditions

your_module/helpers/__init__.py
"""""""""""""""""""""""""""""""
module initializaton, doesn't define or import any sub-modules.

your_module/helpers/config.py
"""""""""""""""""""""""""""""
The following is only required if you have user configurable options.

Imports:

- settings_fields.*
- common.functions.ConfigurationManagerBase
- hirs_admin.models.Setting

**Defines**

.. code-block:: python

    class Config(common.functions.ConfigurationManagerBase):
        root_group = GROUP_CONFIG
        catagory_list = CATAGORY_SETTINGS
        fixtures = CONFIG_DEFAULTS
        Setting = hirs_admin.models.Setting

Additionally define any other classes/function needed to support the configuration for ``your_module``

your_module/helpers/settings_fields.py
""""""""""""""""""""""""""""""""""""""
This module defines how your user configurable settings are defined and how each setting gets rendered.
Each Group, Catagory and Field must be lower case, free of special characters except hyphens and underscores,
all spaces should be replaced with underscores. Durring rendering Groups and Catagories will have the
underscores replaces with spaces and the full string auto capatalized. For more details refer to 
ref: `settings`. Any catogories must have there constant definitions affixed with '_CAT'.

If you have any configurable options, you will need to define this file with the following

:GROUP_CONFIG: *string* Your module name or a descriptive referance which defines your root configuration Group 
:CONFIG_CAT: *string* Your basic configuration Catagory. 
    CONFIG_CAT = "configuration" is only a suggestion, it should be descriptive supporting your modules.
    however you must define at minimum one Catagory must be defined and it's name added to CATAGORY_SETTINGS.
:CATAGORY_SETTINGS: *tuple* A list of your defined Catagories

It is strongly recommended that you define meaningful CONSTANTS for each of your fields to reduce the chance
of typos as they are referanced throught your_module.

:CONFIG_DEFAULTS: *dict* The main iterator that structures your user configurable settings

    | CONFIG_DEFAULTS = {
    |     CONFIG_CAT: {
    |         FIELD_NAME: {
    |             "field_properties": {
    |                 "type": "CharField"
    |             }             
    |         }
    |     }
    | }
    | 

    for a full list of configurable options for field definitions refer to :ref:`settings-field-definitions`

your_module/validators.py
"""""""""""""""""""""""""
Defines ``__all__`` which is a tuple of all defined functions and classes that should be imported globally
whenever ``hris_admin.validators`` is loaded.