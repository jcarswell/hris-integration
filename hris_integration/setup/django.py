# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import string
import importlib
import logging

from random import choice
from pathlib import Path
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management import call_command
from subprocess import run

logger = logging.getLogger("Django Setup Module")


def create_admin(
    username: str = "admin", email: str = "admin@example.com", password: str = None
) -> str:
    username = username or "admin"
    email = email or "admin@example.com"

    qs_email = User.objects.filter(email=email)
    qs_user = User.objects.filter(username=username)
    if len(qs_email) + len(qs_user) == 0:
        logger.debug(f"Creating admin user {username} with email {email}")
        pw = password or "".join(
            choice(string.ascii_letters + string.digits) for char in range(24)
        )
        logger.debug(f"with password: {pw}")
        User.objects.create_superuser(username, email=email, password=pw)
        return pw
    else:
        raise ValueError(
            "An admin account with the specified username or email address"
            "already exists"
        )


def setup(
    service=False,
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = None,
):
    """Once a config file has been created, this function will setup run all the needed
    functions to ensure that the system is ready to roll. This starts by running the
    migrations, creating an admin user, then running any additions configuration needed
    for the installed apps.

    This can be executed as a management command, and run as part of the initial setup or
    as part of the upgrade process.

    :param service: Install the cron service, defaults to False
    :type service: bool, optional
    :param username: The admin account username, defaults to 'admin'
    :type username: str, optional
    :param email: The admin account email, defaults to 'admin@example.com'
    :type email: str, optional
    :param password: The admin account password, defaults to randomly generated password
    :type password: str, optional
    """

    call_command("migrate")

    try:
        logger.debug(
            f"Creating admin user {username} with email {email}"
            f"and password {password}"
        )
        pw = create_admin(username, email, password)
        logger.info(f"Admin password: {pw}")
    except ValueError:
        logger.warn("Admin user already exists")
        pw = None

    for app in settings.INSTALLED_APPS:
        try:
            importlib.import_module(app).setup()
        except ImportError:
            logger.debug(f"Unable to import {app}")
        except AttributeError:
            logger.debug(f"No setup function for {app}")

    from ftp_import.csv import CsvImport

    ftp_headers = Path(settings.BASE_DIR, "ftp_csv_headers.csv")
    if ftp_headers.exists():
        with open(ftp_headers, "r") as f:
            CsvImport(f)

    logger.info("Building Docs")
    run(["sphinx-build.exe", "-b", "html", "../source", "static-core/docs"])
    call_command("collectstatic", interactive=False)

    if service:
        import cron

        cron.install_service()

    if pw:
        logger.info(f"Admin user '{username}' created with password '{pw}'")
