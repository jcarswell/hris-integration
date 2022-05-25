# This Template can be used instead of using the setup script.
# To make use of this template, create a copy of this file and name it config.py.

#
###
### REQUIRED CONFIGURATION
###
#


# The secret key is used for encrypting the session cookies.
SECRET_KEY = None

# The key used for encrypting secret data in the database.
ENCRYPTION_KEY = None

# The hostname or IP address that will be used to access the application.
ALLOWED_HOSTS = [
    #'www.example.com'
]

# The database connection information. Supported backends are:
#  - mssql
#  - django.db.backends.postgresql
#  - django.db.backends.mysql
DATABASE = {
    "ENGINE": "mssql",
    "HOST": "",
    "NAME": "",
    #'USERNAME': '',
    #'PASSWORD': '',
    "OPTIONS": {"driver": "SQL Server Native Client 11.0"},
}

#
###
### OPTIONAL CONFIGURATION
###
#

# The system time zone. (DEFAULT: UTC)
TIME_ZONE = "UTC"

# The directory where static files will be stored. (DEFAULT: static)
# If the path is not absolute, the path will be localized to the app directory.
STATIC_ROOT = "static"

# The URL that will be used to access the static files. Must end with a '/' (DEFAULT: static/)
STATIC_ROOT_URL = "static/"

# The directory where media files will be stored. (DEFAULT: media)
# If the path is not absolute, the path will be localized to the app directory.
MEDIA_ROOT = "media"

# The URL that will be used to access the media files. Must end with a '/' (DEFAULT: media/)
MEDIA_URL = "media/"

# Additional apps to be installed. (DEFAULT: [])
# `corepoint_export` is and optional module representing employee exports that are not to AD.
ADDITIONAL_APPS = ["corepoint_export"]

# The length of password to generate for new employees. (DEFAULT: 12)
PASSWORD_LENGTH = 12

# The characters that will be used in employee password generation.
# (DEFAULT: abcdefABCDEF1234567890!@#$%^&*())
PASSWORD_CHARS = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
