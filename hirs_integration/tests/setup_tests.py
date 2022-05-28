# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import time
from unittest import result

from settings.models import Setting
from pathlib import Path

logger = logging.getLogger("test.setup_tests")


def set_configuration(group: str, config: dict) -> None:
    PATH = group + Setting.FIELD_SEP + "%s" + Setting.FIELD_SEP + "%s"

    for key, val in config.items():
        if type(val) == dict:
            for item, data in val.items():
                try:
                    obj = Setting.o2.get(setting=PATH % (key, item))
                    obj.value = data
                    obj.save()
                except Setting.DoesNotExist:
                    logger.exception("WHAT THE FUCK: " + PATH % (key, item))
                    raise Exception("Wham!")


def setup_word_mapping():
    from settings.models import WordList

    logger.info("Setting up word mappings")

    wl = {"mgr": "Manager", "Dir": "Director"}

    for key, val in wl.items():
        w, _ = WordList.objects.get_or_create(src=key)
        w.replace = val
        w.save()


def setup_group_mapping():
    from organization.models import JobRole, BusinessUnit, Location, GroupMapping

    logger.info("Setting up Group Mappings")
    logger.warn("They will needed to be changed before working during an AD export")
    job = GroupMapping()
    job.dn = "CN=test group,CN=users,DC=example,DC=net"
    job.jobs.add(JobRole.objects.last())
    job.save()

    job_not = GroupMapping()
    job_not.dn = "CN=test not job,CN=users,DC=example,DC=net"
    job_not.jobs.add(JobRole.objects.first())
    job_not.jobs_not = True
    job_not.save()

    loc = GroupMapping()
    loc.dn = "CN=test location,CN=users,DC=example,DC=net"
    loc.location.add(Location.objects.last())
    loc.save()

    bu = GroupMapping()
    bu.dn = "CN=test bu,CN=users,DC=example,DC=net"
    bu.business_unit.add(BusinessUnit.objects.last())
    bu.save()

    all = GroupMapping()
    all.all = True
    all.dn = "CN=test all,CN=users,DC=example,DC=net"
    all.save()


def setup_ftp_import():
    from ftp_import.helpers import config

    logger.info("Setting up FTP Import Configuration")

    module_config = {
        config.CAT_SERVER: {
            config.SERVER_SERVER: None,
            config.SERVER_PROTOCOL: "sftp",
            config.SERVER_PORT: "22",
            config.SERVER_USER: None,
            config.SERVER_PASSWORD: None,
            config.SERVER_SSH_KEY: None,
            config.SERVER_PATH: ".",
            config.SERVER_FILE_EXP: ".*",
        },
        config.CAT_CSV: {
            config.CSV_FIELD_SEP: ",",
            config.CSV_FAIL_NOTIF: "",
            config.CSV_IMPORT_CLASS: "ftp_import.forms",
            config.CSV_USE_EXP: "True",
        },
        config.CAT_FIELD: {
            config.FIELD_LOC_NAME: "ll4_desc",
            config.FIELD_JD_NAME: "ll7_desc",
            config.FIELD_JD_BU: "ll5",
            config.FIELD_BU_NAME: "ll5_desc",
            config.FIELD_BU_PARENT: None,
            config.FIELD_STATUS: "employee_status",
        },
        config.CAT_EXPORT: {
            config.EXPORT_ACTIVE: "AC",
            config.EXPORT_TERM: "TER",
            config.EXPORT_LEAVE: "L",
        },
    }

    set_configuration(config.GROUP_CONFIG, module_config)

    fields = config.get_fields()
    field_conf = {
        "employee_number": "id",
        "first_name": "first_name",
        "last_name": "last_name",
        "employee_status": "status",
        "address": "street1",
        "city": "city",
        "province": "province",
        "zip": "postal_code",
        "country": "country",
        "phone_1": "number",
        "ll7": "primary_job",
        "ll4": "location",
        "reports_to": "manager",
        "secondarylabour": "secondary_jobs",
    }

    for key, value in field_conf.items():
        if key in fields.keys():
            s = Setting.objects.get_by_path(config.GROUP_MAP, key, "map_to")
            try:
                s = s[0]
                s.value = value
                s.save()
                s = Setting.objects.get_by_path(config.GROUP_MAP, key, "import")
                s = s[0]
                s.value = "True"
                s.save()

            except IndexError:
                logger.warning(f"field {key} doesn't exists")


def setup_ad_export():
    from ad_export.helpers import config

    logger.info("Setting up AD Export")
    print("\nPlease set your upn domain and route address\n")
    while True:
        route_address = input("Enter your routing address: ")
        if route_address:
            break
    while True:
        upn_domain = input("UPN Domain: ")
        if upn_domain:
            break

    module_config = {
        config.CONFIG_CAT: {
            config.CONFIG_NEW_NOTIFICATION: "",
            config.CONFIG_UPN: upn_domain,
            config.CONFIG_ROUTE_ADDRESS: route_address,
            config.CONFIG_ENABLE_MAILBOXES: "True",
            config.CONFIG_MAILBOX_TYPE: "remote",
            config.CONFIG_LAST_SYNC: "1999-01-01 00:00",
        },
        config.EMPLOYEE_CAT: {
            config.EMPLOYEE_DISABLE_LEAVE: "False",
            config.EMPLOYEE_LEAVE_GROUP_ADD: "active user",
            config.EMPLOYEE_LEAVE_GROUP_DEL: "leave user",
        },
        config.DEFAULTS_CAT: {
            config.DEFAULT_ORG: "Constco",
            config.DEFAULT_PHONE: "",
            config.DEFAULT_FAX: "",
            config.DEFAULT_STREET: "123 Harlem Ave",
            config.DEFAULT_PO: "",
            config.DEFAULT_CITY: "Regina",
            config.DEFAULT_STATE: "Saskatchewan",
            config.DEFAULT_ZIP: "S4S 4S4",
            config.DEFAULT_COUNTRY: "CA",
        },
    }

    set_configuration(config.GROUP_CONFIG, module_config)


def setup_smtp():
    from smtp_client.helpers import config

    logger.info("Setting up SMTP Client")
    print("\nPlease set your defaults for testing\n")
    server = input("SMTP Server [localhost]: ")
    if not server:
        server = "localhost"
    port = input("SMTP Port [25]: ")
    if not port:
        port = "25"
    tls = input("TLS [y/N]: ").lower()
    if not tls or tls == "n":
        tls = "False"
    else:
        tls = "True"
    ssl = input("SSL [y/N]: ", "N").lower()
    if not ssl or ssl == "n":
        ssl = "False"
    else:
        ssl = "True"
    username = input("Username []: ")
    password = input("Password []: ")
    sender = input("Sender [hris_admin@example.com]: ")
    if not sender:
        sender = "hris_admin@example.com"

    module_config = {
        config.CAT_CONFIG: {
            config.SERVER_SERVER: server,
            config.SERVER_PORT: port,
            config.SERVER_TLS: tls,
            config.SERVER_SSL: ssl,
            config.SERVER_USERNAME: username,
            config.SERVER_PASSWORD: [password, True],
            config.SERVER_SENDER: sender,
        },
    }

    set_configuration(config.GROUP_CONFIG, module_config)


def import_employees():
    import tests.test_import
    from unittest import TestResult

    result = TestResult()
    tests.test_import.run(result=result)
    logger.info(f"{result.testsRun} tests run")


def run_ad_export():
    import ad_export

    ad_export.run()


def run_setup():
    import setup

    logger.info("Running setup")
    setup.setup(service=False)
    setup_word_mapping()
    setup_ftp_import()
    setup_ad_export()
    g = input("Run employee import [Y/n]: ").lower()
    if not g or g == "y":
        import_employees()
        setup_group_mapping()


def send_email(dest: str = None):
    from smtp_client import smtp

    logger.info("Sending test text email")

    if dest is None:
        dest = input(f"Send Test Email to: ")
    s = smtp.Smtp()
    s.send(
        dest, "Test email sent from setup_tests.send_email()", "HRIS Sync Test Email"
    )


def send_email_html(dest: str = None):
    from smtp_client import smtp

    logger.info("Sending test html email")

    if dest is None:
        dest = input(f"Send Test Email to: ")
    s = smtp.Smtp()
    msg = s.mime_build(
        "Test email sent from setup_tests.send_email()",
        "<p>Test email sent from setup_tests<i>.send_email()</i></p>",
        "HRIS Sync Test Email",
        dest,
    )
    s.send_html(dest, msg)
