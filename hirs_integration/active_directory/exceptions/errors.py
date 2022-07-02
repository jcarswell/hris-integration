# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.exceptions import HrisIntegrationBaseError
from pyad.pyadexceptions import (
    noExecutedQuery,
    invalidResults,
    InvalidAttribute,
    InvalidObjectException,
    noObjectFoundException,
    invalidOwnerException,
    win32Exception,
    genericADSIException,
    comException,
)


class ActiveDirectoryError(HrisIntegrationBaseError):
    pass


class TooManyResults(ActiveDirectoryError):
    def __init__(self, *args: object, result_count: int = None) -> None:
        self.result_count = result_count
        super().__init__(*args)


class Error(ActiveDirectoryError):
    """
    This is the base class for all Active Directory interface errors. All errors are
    derived as per the PEP-249 specification.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Warning(ActiveDirectoryError):
    """
    This is the base class for all Active Directory interface warnings. All warnings are
    derived as per the PEP-249 specification.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InterfaceError(Error):
    """
    Exception raised for errors that are related to the database interface rather than
    the database itself.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DatabaseError(Error):
    """
    Exception raised for errors that are related to the database.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DataError(DatabaseError):
    """
    Exception raised for errors that are due to problems with the processed data like
    division by zero, numeric value out of range, etc.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class OperationalError(DatabaseError):
    """
    Exception raised for errors that are related to the database's operation and not
    necessarily under the control of the programmer, e.g. an unexpected disconnect
    occurs, the data source name is not found, a transaction could not be processed,
    a memory allocation error occurred during processing, etc.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IntegrityError(DatabaseError):
    """
    Exception raised when the relational integrity of the database is affected, e.g. a
    foreign key check fails.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InternalError(DatabaseError):
    """
    Exception raised when the database encounters an internal error, e.g. the cursor is
    not valid anymore, the transaction is out of sync, etc.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ProgrammingError(DatabaseError):
    """
    Exception raised for programming errors, e.g. table not found or already exists,
    syntax error in the statement, wrong number of parameters specified, etc.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotSupportedError(DatabaseError):
    """
    Exception raised in case a method or database API was used which is not supported
    by the database, e.g. requesting a .rollback() on a connection that does not support
    transaction or has transactions turned off.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
