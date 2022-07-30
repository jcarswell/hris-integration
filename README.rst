HRIS Synchronization System
***************************

HRIS Synchronization System is developed to act as a go between for HRIS
system that only dumps employee data to a csv file hosted on a sftp site.
This system once configured will fetch the latest files from the sftp 
server and and import them using the configured csv form. it will then
take that data and export it to active directory.

Issues: https://git.ttdev.ca/hris-sync/hris-integration/-/issues

Setting up
==========

Replace the ftp_csv_headers.csv file in the hris_integration folder
with the headers from your csv dump. If your csv file does not use the
standard ',' separator, don't fret, you can change this later in the 
settings.

1. Install the requirements ``pip install -r requirements.txt``
2. From the hris_integration folder run ``python -m setup --db-host=<host> --db-name=<name>``
    By default the setup will configure to use MSSQL server as the database and assumes
    the user/service account has access to the database. If you need to specify a username
    and password, you can do so by passing the --db-username and --db-password flags.

    If you wish to use mysql or postgresql, you can do so by passing the --database flag.

    As part of the setup process, the default admin account will be created, if you wish
    to configure this user, you can do so by passing the --adm-username, --adm-email, and
    --admin-password flags.
    
    For full configuration options, run python -m setup --help

3. You may wish to review the configuration file, hris_integration/config.py
   and change any settings you wish.
4. From the hris_integration folder run `manage.py runsetup`
5. `Configure IIS for python web apps <https://docs.microsoft.com/en-us/visualstudio/python/configure-web-apps-for-iis-windows?view=vs-2019>`
6. Login to the web interface with the credentials printed during setup
7. Configure you settings and add your word expansions
8. Manually run the jobs to verify everything is configured correctly

    .. code-block:: python
    
        manage.py runftpimport
        manage.py runadexpoprt


   - After running the ftp import you may wish to review employees to ensure that there
     are no changes that need to be applied to users before they are pushed to active directory.
     Additionally you may wish to perform group mappings and software account bindings.

11. configure scheduled jobs to run the ftp import and ad export jobs as desired.


Release Notes
=============

0.3.1 - Import Issues
---------------------

This is a bug fix release. Importing employees would result in errors being thrown for
saving phone numbers and addresses, due the fact that the pk of all models is now id.

There is a known issues with the employee page for adding phone numbers and addresses, 
then trying to set them as primary, which will cause that page to be reloaded as the
submit hook is not registering correctly. To work around this issue, simply refresh the
page after you have added and phone number or addresses, then check the primary checkbox.

0.3.0 - Quality of Life improvements and Github release
-------------------------------------------------------

*Important Notes*

- The project folder name has been re-named to hris_integration
- This is a major release and an major overhaul of the code base
- v0.3 will be a required release before migrating to future versions
- Primary Addresses and Phone Numbers are now exported to AD, if no address is set
    as a primary then no address is exported. By default addresses and phone numbers
    imported are not marked as primary.
- If there are employees pending import, they will be deleted if you wish, resolve these
    before running the setup, otherwise they will be re-added to the system during the
    next import
- There is no longer a pending employee's section, these employees are now found on the
    employees page and are marked as pending
- Before you upgrade, please review your FTP field mappings and corepoint field mappings
    as there was field changes that may have unintended side effects

This is a release is a much needed overhaul of the Employee database enabling full
control over the employee instance and no longer treats pending employees as an 
afterthought. This was a needed change to allow for the User Account tracking 
functionality as it would have defeated the purpose of the feature, it also enables
you to track addresses and phones to pending employees removing the requirement that
they needed to be imported from the HRIS system first.

Additional Features:

- There is now a password generator that is configurable in the config.py.

    by default the password generator generates a 12 character password, composed of
    non-conflicting letters and numbers.

- There is now an global employee manager, this manager will load up the AD user upon
    initialization allowing for the retrieval of current employee data as set in AD.
- Where supported you now have the option of Create + New instead of Create which takes
    you to the instance page where further configuration is possible.
- Employee Photo uploads are now supported, currently this only stores the files, in a 
    future release this will also upload the files to AD.
- The user account tracking system allows for the binding software instances to AD group
    allowing for the enablement of software enable AD groups.
- There is now an API! The documentation is available at https://<you.url>/api/swagger/
- Documentation is now available at https://<you.url>/static/docs/index.html (this is a
    work in progress, and will be published to read the docs in the future)

Deprecation Notes:

v0.4 will remove the get_config functions as well as legacy fields firstname, lastname,
givenname and surname. these are all replaced with first_name and last_name. Additionally
legacy id fields will be removed, these are all replaced by id.


0.2.0 - Settings Improvements
-----------------------------

*Important Notes*

- settings.py has been updated, so be sure to back up your keys before updating
- Requirements update. (Optional but recommended) Run ``pip install -r requirements.txt --upgrade``

This release brings numerous improvements and fixes. The highlighting feature is a 
complete overhaul of the settings area, this include drop down for field matching 
check marks for boolean fields and more. When accessing Settings data there is a 
new ConfigManager class which will retrieve the setting value and return the 
appropriate type, instead the stored string value. There is now a option to perform 
manual imports and matching from the pending imports page. Most multi-select fields 
have been updated to use SelectPicker bootstrap module.

Bug fixes include:

- Alert messages now function across all forms
- Overall UI layout enhancements/formatting corrections
- Re-running ad_export or corepoint_export in the same day would result in no changes detected.
- Email sending

Copyright
=========

HRIS Synchronization System is licensed under GNU GLP v3
Copyright 2022 Josh Carswell