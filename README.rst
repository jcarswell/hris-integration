HRIS Syncronization System
**************************

HRIS Synconization System is developed to act as a go between for hirs
system that only dumps employee data to a csv file hosted on a sftp site.
This system once configued will fetch the latest files from the sftp 
server and and import them using the configured csv form. it will then
take that data and export it to active directory.

Setting up
==========

Replace the ftp_csv_headers.csv file in the hirs_integration folder
with the headers from your csv dump. If your csv file does not use the
standard ',' seporator, don't fret, you can change this later in the 
settings.
1. Intall the requirements ``pip install -r requirments.txt``
2. from the hirs_integraton folder run ``python`` and paste the following
   
    .. code-block:: python

        import setup
        setup.create_keys()
        exit()

3. Paste the two gernerated lines into hirs_integraion\hirs_integration\settings.py
4. Setup your database configuration in hirs_integraion\hirs_integration\settings.py
5. From the hirs_integraton folder run `manage.py migrate`
6. From the hirs_integraton folder run `manage.py runsetup`
7. `Configure IIS for python web apps <https://docs.microsoft.com/en-us/visualstudio/python/configure-web-apps-for-iis-windows?view=vs-2019>`
8. Login to the web interface with the credentials printed during setup
9. Configure you settings and add your word expansions
10. Manually run the jobs to verify everything is configued correctly

    .. code-block:: python
    
        manage.py runftpimport
        manage.py adexpoprt


   - You may want to configure overrides for employees before running the import

11. Enable Cron in the settings

Release Notes
=============

0.2.0 - Settings Improvments
----------------------------

*Important Notes*
- settings.py has been updated, so be sure to back up your keys before updating
- Requiremets update. (Optional but recommended) Run ``pip install -r requirements.txt --updgrade``

This release brings numerous improvments and fixes. The highlighting feature is a copmlete overhaul of the settings area, this include drop down for field matching checkmarks for boolean fields and more. When accessing Settings data there is a new ConfigManager class which will retrieve the setting value and return the appropriate type, instead the stored string value. There is now a option to perform manual imports and matching from the pending imports page. Most multi-select fields have been updated to use SelectPicker bootstrap module.
Bug fixes include:
- Alert messages now function across all forms
- Overall UI layout enhancements/formatting corrections
- Re-running ad_export or corepoint_export in the same day would result in no changes detected.
- Email sending

Copyright
=========

HRIS Syncronization System is licenesed under GNU GLP v3
copyright 2021 Josh Carswell