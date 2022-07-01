# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from pyad import ADQuery, ADUser
from active_directory.exceptions import TooManyResults

logger = logging.getLogger("active_directory.search")


def get_by_employee_id(id: int, base_dn: str = None) -> ADUser:
    """
    Get an AD User object based on their employee id

    :param id: The Employee ID to search
    :type id: int
    :param base_dn: the base path to search within, defaults to None
    :type base_dn: str, optional
    :return: The ADUser matching the query
    :rtype: ADUser
    """

    q = ADQuery()
    q.execute_query(
        where_clause="employeeNumber = '%d' or employeeID = '%d'" % (id, id),
        base_dn=base_dn,
    )
    if len(q) > 1:
        raise TooManyResults(result_count=len(q))
    elif len(q) == 1:
        return ADUser.from_dn(q.get_single_result()["distinguishedName"])

    return None


def get_by_username(username: str, base_dn: str = None) -> ADUser:
    """
    Get an AD User by sAMAccountName (username)

    :param username: the username to retrieve
    :type username: str
    :param base_dn: the base path to search within, defaults to None
    :type base_dn: str, optional
    :raises TooManyResults: If more than one result is found
    :return: The ADUser matching the query
    :rtype: ADUser
    """

    q = ADQuery()
    q.execute_query(
        where_clause="sAMAccountName = '%s'" % username,
        base_dn=base_dn,
    )
    if len(q) > 1:
        raise TooManyResults(result_count=len(q))
    elif len(q) == 1:
        return ADUser.from_dn(q.get_single_result()["distinguishedName"])

    return None


def get_by_upn(upn: str, base_dn: str = None) -> ADUser:
    """
    Get an AD User by userPrincipalName

    :param upn: the userPrincipalName to retrieve
    :type upn: str
    :param base_dn: the base path to search within, defaults to None
    :type base_dn: str, optional
    :raises TooManyResults: If more than one result is found
    :return: The ADUser matching the query
    :rtype: ADUser
    """

    q = ADQuery()
    q.execute_query(
        where_clause="userPrincipalName = '%s'" % upn,
        base_dn=base_dn,
    )
    if len(q) > 1:
        raise TooManyResults(result_count=len(q))
    elif len(q) == 1:
        return ADUser.from_dn(q.get_single_result()["distinguishedName"])

    return None


def get_by_guid(guid: str) -> ADUser:
    """
    A wrapper function for the native from_guid method

    :param guid: the guid to retrieve
    :type guid: str

    :return: The ADUser matching the query
    :rtype: ADUser
    """

    return ADUser.from_guid(guid)
