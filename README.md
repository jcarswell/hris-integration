# HIRS Syncronization System
HIRS Synconization System is developed to act as a go between for hirs
system that only dumps employee data to a csv file hosted on a sftp site.
This system once configued will fetch the latest files from the sftp 
server and and import them using the configured csv form. it will then
take that data and export it to active directory.

## Setting up
Replace the ftp_csv_headers.csv file in the hirs_integration folder
with the headers from your csv dump. If your csv file does not use the
standard ',' seporator, don't fret, you can change this later in the 
settings.
1. Intall the requirements `pip install -r requirments.txt`
2. from the hirs_integraton folder run `python` and paste the following
    ```
    import setup
    setup.create_keys()
    exit()
    ```
3. Paste the two gernerated lines into hirs_integraion\hirs_integration\settings.py
4. Setup your database configuration in hirs_integraion\hirs_integration\settings.py
5. From the hirs_integraton folder run `manage.py migrate`
6. From the hirs_integraton folder run `manage.py runsetup`
7. https://docs.microsoft.com/en-us/visualstudio/python/configure-web-apps-for-iis-windows?view=vs-2019[Configure IIS for python web apps]
8. Login to the web interface with the credentials printed during setup
9. Configure you settings and add your word expansions
10. Manually run the jobs to verify everything is configued correctly
   ```
   manage.py runftpimport
   manage.py adexpoprt
   ```
   - You may want to configure overrides for employees before running the import
11. Enable Cron in the settings

## Copyright
HIRS Syncronization System is licenesed under GNU GLP v3
copyright 2021 West Country Hosting

## Overriding import/export forms
Where the configuration allows for it, an import/export form or module may be overridden
to accomidate custom configuration. To do this setup a custom module that  will either be
in the root directory of the Django app or will be installed into your global path.

Your form will extend the base class with provides most of the basic interfaces and data.
You will need to define the run method which is what will be called after class initalization.

Once you have built your class you will need to define add a form variable that points to your
custom class.

If you have not worked with Django before, the app root is added to the path. When you are importing
other classes you would not use hirs_integration.module, instead you just call the module directly.

Base Froms:
- ftp_import: ftp_import.forms.BaseImport
- corepoint_export: corepoint_export.forms.BaseExport

An example module would look something like:
```
from ftp_import.forms import BaseImport
Class MyImportClass(BaseImport):
    def run(self):
        for key,value in self.kwargs:
            if hasattr(self.employee):
                setattr(self.employee,key,value)

form = MyImportClass
```

Now update the config to be the import path for your form