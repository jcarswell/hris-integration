# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import re
import pyodbc
import logging

from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _t
from django.db import utils
from .helpers.config import CONFIG_CAT, BASE_DN, get_config
from .query import Query
from pyad import ADUser

logger = logging.getLogger("active_directory.validators")

__all__ = ("DnValidator", "ad_groups", "ad_ous")

INIT_ERROR = [("Not Loaded", "System not initialized")]


class DnValidator(RegexValidator):
    regex = (r"^((CN=([^,]*)),)?((((?:CN|OU)=[^,]+,?)+),)?((DC=[^,]+,?)+)$",)
    message = _t("Not a valid DN string")
    flags = re.IGNORECASE


def ad_groups(dn=None):
    ad_query = Query()

    try:
        base_dn = dn or get_config(CONFIG_CAT, BASE_DN)
        ad_query.execute_query(
            attributes=["name", "distinguishedName"],
            where_clause="objectClass = 'group'",
            base_dn=base_dn,
        )

        return [(None, "")] + ad_query.get_all_results_tuple()
    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except AttributeError:
        logger.info("Caught Attribute Error, this is likely due to pre-init")
        return INIT_ERROR


def ad_ous(dn=None):
    ad_query = Query()
    output = [(None, "")]
    try:
        base_dn = dn or get_config(CONFIG_CAT, BASE_DN)
        ad_query.execute_query(
            attributes=["distinguishedName"],
            where_clause="objectCategory = 'organizationalUnit'",
            base_dn=base_dn,
        )

        res = ad_query.get_all_results()
        for r in res:
            output.append((r["distinguishedName"], r["distinguishedName"]))

        return output
    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except AttributeError:
        logger.info("Caught Attribute Error, this is likely due to pre-init")
        return INIT_ERROR


def ad_user_dn(dn=None):
    ad_query = Query()
    users = [(None, "")]
    try:
        base_dn = dn or get_config(CONFIG_CAT, BASE_DN)
        ad_query.execute_query(
            attributes=["distinguishedName", "objectClass"],
            where_clause="objectClass = 'user'",
            base_dn=base_dn,
        )

        for user in ad_query.get_results():
            if user["objectClass"] != "computer":
                u = ADUser.from_dn(user["distinguishedName"])
                users.append((u.name, user["distinguishedName"]))

        return users
    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except AttributeError:
        logger.info("Caught Attribute Error, this is likely due to pre-init")
        return INIT_ERROR


def ad_user_guid(dn=None):
    ad_query = dn or Query()
    users = [(None, "")]
    try:
        base_dn = get_config(CONFIG_CAT, BASE_DN)
        ad_query.execute_query(
            attributes=["distinguishedName", "objectClass"],
            where_clause="objectClass = 'user'",
            base_dn=base_dn,
        )

        for user in ad_query.get_results():
            if user["objectClass"] != "computer":
                u = ADUser.from_dn(user["distinguishedName"])
                users.append((u.name, u.guid_str))

        return users

    except pyodbc.ProgrammingError:
        logger.warning("Caught pyodbc.ProgrammingError")
        return INIT_ERROR
    except utils.ProgrammingError:
        logger.warning("Caught django.utils.ProgrammingError")
        return INIT_ERROR
    except AttributeError:
        logger.info("Caught Attribute Error, this is likely due to pre-init")
        return INIT_ERROR
