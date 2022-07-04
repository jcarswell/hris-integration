import sys
import os
from pathlib import Path
import argparse

from setup import config
from django.core.exceptions import ImproperlyConfigured

if sys.version_info.major < 3 and sys.version_info.minor < 8:
    print("Python 3.8 or higher is required to run this application.")
    sys.exit(1)

CONFIG_PATH = os.getenv(
    "CONFIG_PATH",
    Path(Path(sys.argv[0]).resolve().parent.parent, "hris_integration").resolve(),
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hris_integration.settings")

argparser = argparse.ArgumentParser(
    prog="HRIS Integration Setup",
    description="The setup utility for the HRIS Integration application.",
)

argparser.add_argument(
    "--database",
    type=str,
    choices=config.DATABASE_CHOICES,
    help="The Database backend to use.",
)
argparser.add_argument("--db-host", type=str, help="The database hostname")
argparser.add_argument("--db-port", type=int, help="The database port")
argparser.add_argument("--db-name", type=str, help="The database name")
argparser.add_argument("--db-username", type=str, help="The database username")
argparser.add_argument("--db-password", type=str, help="The database password")
argparser.add_argument(
    "--secret-key", type=str, help="The secret key, if you have one already"
)
argparser.add_argument(
    "--encryption-key", type=str, help="The encryption key, if you have one already"
)
argparser.add_argument("--media-root", type=str, help="The uploaded media root")
argparser.add_argument("--media-url", type=str, help="The uploaded media url")
argparser.add_argument("--static-root", type=str, help="The static root")
argparser.add_argument("--static-url", type=str, help="The static url")
argparser.add_argument(
    "--allowed-hosts",
    type=str,
    help='The hostname of the application, example "hris-sync.company.com"',
)
argparser.add_argument("--time-zone", type=str, help="The time zone of the application")
argparser.add_argument(
    "--adm_email",
    type=str,
    default="admin@example.com",
    help="The email address of the admin user",
)
argparser.add_argument(
    "--adm_password",
    type=str,
    default=None,
    help="The password of the admin user, if not set a random password will be generated",
)
argparser.add_argument(
    "--adm_username", type=str, default="admin", help="The username of the admin user"
)

args = vars(argparser.parse_args())
print(args)

#### Stupid argument parsing
ARGS_MAP = {
    "HOST": "db_host",
    "PORT": "db_port",
    "NAME": "db_name",
    "USERNAME": "db_username",
    "PASSWORD": "db_password",
    "MEDIA_ROOT": "media_root",
    "MEDIA_URL": "media_url",
    "STATIC_ROOT": "static_root",
    "STATIC_URL": "static_url",
    "ALLOWED_HOSTS": "allowed_hosts",
    "TIME_ZONE": "time_zone",
    "ENCRYPTION_KEY": "encryption_key",
    "SECRET_KEY": "secret_key",
}

db: dict = config.DATABASE_CHOICE_MAP[getattr(args, "database", "mssql")]
set_db = False

for key in ["HOST", "PORT", "NAME", "USERNAME", "PASSWORD"]:
    if args[ARGS_MAP[key]]:
        db[key] = args[ARGS_MAP[key]]
        set_db = True

if set_db:
    config.DEFAULTS["DATABASE"] = db

for key in [
    "SECRET_KEY",
    "ENCRYPTION_KEY",
    "MEDIA_ROOT",
    "MEDIA_URL",
    "STATIC_ROOT",
    "STATIC_URL",
    "ALLOWED_HOSTS",
    "TIME_ZONE",
]:
    if args[ARGS_MAP[key]]:
        config.DEFAULTS[key] = args[ARGS_MAP[key]]

print(f"Writing configuration to {CONFIG_PATH}")
cont = config.config(CONFIG_PATH)

if cont:
    print(f"Configuration file written to {str(CONFIG_PATH)}/config.py")
    import django

    try:
        django.setup()
        from setup.django import setup

        setup(
            username=args["adm_username"],
            password=args["adm_password"],
            email=args["adm_email"],
        )
    except ImproperlyConfigured as e:
        print("Please confirm you configuration is correct and try again.")
        print(e)

else:
    print(
        "Configuration file written to {str(CONFIG_PATH)}/config.py however additional "
        "configuration is required."
    )
