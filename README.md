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