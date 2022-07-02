# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Tuple, Dict, AnyStr

from .errors import (
    Error,
    Warning,
    InterfaceError,
    DatabaseError,
    DataError,
    IntegrityError,
    InternalError,
    ProgrammingError,
    NotSupportedError,
    OperationalError,
)

AD_EXCEPTIONS: Dict[hex, Tuple[AnyStr, AnyStr, Error]] = {
    "0x8007202f": (
        "LDAP_CONSTRAINT_VIOLATION",
        "The object is not valid for the given operation.",
        IntegrityError,
    ),
    "0x80071392": (
        "LDAP_ALREADY_EXISTS",
        "The Object Already Exists.",
        ProgrammingError,
    ),
    "0x8007202b": ("LDAP_REFERRAL", "A referred object is found.", DataError),
    "0x80070005": (
        "LDAP_INSUFFICIENT_RIGHTS",
        "The user does not have sufficient rights to perform the operation.",
        InterfaceError,
    ),
    "0x80070008": ("LDAP_NO_MEMORY", "The server ran out of memory.", OperationalError),
    "0x8007001f": ("LDAP_OTHER", "An unknown error occurred.", OperationalError),
    "0x800700ea": (
        "LDAP_PARTIAL_RESULTS|LDAP_MORE_RESULTS_TO_RETURN",
        "Partial results and referrals received. There may be more results to return.",
        InterfaceError,
    ),
    "0x800704c7": (
        "LDAP_USER_CANCELLED",
        "User canceled the operation",
        OperationalError,
    ),
    "0x800704c9": (
        "LDAP_CONNECT_ERROR",
        "Cannot establish the connection",
        InterfaceError,
    ),
    "0x8007052e": (
        "LDAP_INVALID_CREDENTIALS",
        "Supplied credential is not valid",
        InterfaceError,
    ),
    "0x800705b4": ("LDAP_TIMEOUT", "Search timed out", InterfaceError),
    "0x8007200a": (
        "LDAP_NO_SUCH_ATTRIBUTE",
        "Requested attribute does not exist",
        ProgrammingError,
    ),
    "0x8007200b": ("LDAP_INVALID_SYNTAX", "Syntax is not valid", ProgrammingError),
    "0x8007200c": ("LDAP_UNDEFINED_TYPE", "Type not defined", DataError),
    "0x8007200d": (
        "LDAP_ATTRIBUTE_OR_VALUE_EXISTS",
        "Attribute exists or the value has been assigned",
        DataError,
    ),
    "0x8007200e": ("LDAP_BUSY", "Server is busy", InterfaceError),
    "0x8007200f": ("LDAP_UNAVAILABLE", "Server is not available", InterfaceError),
    "0x80072014": (
        "LDAP_OBJECT_CLASS_VIOLATION",
        "Object class violation",
        IntegrityError,
    ),
    "0x80072015": (
        "LDAP_NOT_ALLOWED_ON_NONLEAF",
        "Operation is not allowed on a non-leaf object",
        InterfaceError,
    ),
    "0x80072016": (
        "LDAP_NOT_ALLOWED_ON_RDN",
        "Operation is not allowed on an RDN",
        InterfaceError,
    ),
    "0x80072017": (
        "LDAP_NO_OBJECT_CLASS_MODS",
        "Cannot modify object class",
        IntegrityError,
    ),
    "0x80072020": (
        "LDAP_OPERATIONS_ERROR",
        "Operation error occurred",
        OperationalError,
    ),
    "0x80072021": ("LDAP_PROTOCOL_ERROR", "Protocol error occurred", InterfaceError),
    "0x80072022": ("LDAP_TIMELIMIT_EXCEEDED", "Exceeded time limit", OperationalError),
    "0x80072023": ("LDAP_SIZELIMIT_EXCEEDED", "Exceeded size limit", OperationalError),
    "0x80072024": (
        "LDAP_ADMIN_LIMIT_EXCEEDED",
        "Exceeded administration limit on the server",
        OperationalError,
    ),
    "0x80072027": (
        "LDAP_AUTH_METHOD_NOT_SUPPORTED",
        "The authentication method is not supported",
        InterfaceError,
    ),
    "0x80072028": (
        "LDAP_STRONG_AUTH_REQUIRED",
        "Strong authentication is required",
        InterfaceError,
    ),
    "0x80072029": (
        "LDAP_INAPPROPRIATE_AUTH",
        "Authentication is inappropriate",
        InterfaceError,
    ),
    "0x8007202a": (
        "LDAP_AUTH_UNKNOWN",
        "Unknown authentication error occurred",
        InterfaceError,
    ),
    "0x8007202c": (
        "LDAP_UNAVAILABLE_CRIT_EXTENSION",
        "Critical extension is unavailable",
        InternalError,
    ),
    "0x8007202d": (
        "LDAP_CONFIDENTIALITY_REQUIRED",
        "Confidentiality is required",
        NotSupportedError,
    ),
    "0x8007202e": (
        "LDAP_INAPPROPRIATE_MATCHING",
        "There was an inappropriate matching",
        ProgrammingError,
    ),
    "0x80072030": ("LDAP_NO_SUCH_OBJECT", "Object does not exist", ProgrammingError),
    "0x80072031": ("LDAP_ALIAS_PROBLEM", "Alias is not valid", IntegrityError),
    "0x80072032": (
        "LDAP_INVALID_DN_SYNTAX",
        "Distinguished name has syntax that is not valid",
        DataError,
    ),
    "0x80072033": ("LDAP_IS_LEAF", "The object is a leaf", Warning),
    "0x80072034": (
        "LDAP_ALIAS_DEREF_PROBLEM",
        "Cannot dereference the alias",
        IntegrityError,
    ),
    "0x80072035": (
        "LDAP_UNWILLING_TO_PERFORM",
        "Server cannot perform operation",
        OperationalError,
    ),
    "0x80072036": ("LDAP_LOOP_DETECT", "Loop was detected", DataError),
    "0x80072037": (
        "LDAP_NAMING_VIOLATION",
        "There was a naming violation",
        IntegrityError,
    ),
    "0x80072038": (
        "LDAP_RESULTS_TOO_LARGE",
        "Results set is too large",
        InterfaceError,
    ),
    "0x80072039": (
        "LDAP_AFFECTS_MULTIPLE_DSAS",
        "Multiple directory service agents are affected",
        InternalError,
    ),
    "0x8007203a": (
        "LDAP_SERVER_DOWN",
        "Cannot contact the LDAP server",
        InterfaceError,
    ),
    "0x8007203b": ("LDAP_LOCAL_ERROR", "Local error occurred", InternalError),
    "0x8007203c": ("LDAP_ENCODING_ERROR", "Encoding error occurred", DataError),
    "0x8007203d": ("LDAP_DECODING_ERROR", "Decoding error occurred", DataError),
    "0x8007203e": ("LDAP_FILTER_ERROR", "The search filter is bad", ProgrammingError),
    "0x8007203f": (
        "LDAP_PARAM_ERROR",
        "A bad parameter was passed to a function",
        ProgrammingError,
    ),
    "0x80072040": ("LDAP_NOT_SUPPORTED", "Feature not supported", NotSupportedError),
    "0x80072041": (
        "LDAP_NO_RESULTS_RETURNED",
        "Results are not returned",
        InternalError,
    ),
    "0x80072042": (
        "LDAP_CONTROL_NOT_FOUND",
        "Control was not found",
        NotSupportedError,
    ),
    "0x80072043": ("LDAP_CLIENT_LOOP", "Client loop was detected", OperationalError),
    "0x80072044": (
        "LDAP_REFERRAL_LIMIT_EXCEEDED",
        "Exceeded referral limit",
        OperationalError,
    ),
    "0x80004004": ("E_ABORT", "Operation aborted", InternalError),
    "0x80004005": ("E_FAIL", "Unspecified error", InternalError),
    "0x80004002": ("E_NOINTERFACE", "Interface not supported", InterfaceError),
    "0x80004001": ("E_NOTIMPL", "Not implemented", NotImplementedError),
    "0x80004003": ("E_POINTER", "Invalid pointer", ProgrammingError),
    "0x8000FFFF": ("E_UNEXPECTED", "Catastrophic failure.", InternalError),
    "0x00005011": (
        "S_ADS_ERRORSOCCURRED",
        "During a query, one or more errors occurred",
        InternalError,
    ),
    "0x00005012": (
        "S_ADS_NOMORE_ROWS",
        "The search operation has reached the last row",
        DataError,
    ),
    "0x00005013": (
        "S_ADS_NOMORE_COLUMNS",
        "The search operation has reached the last column for the current row",
        DataError,
    ),
    "0x80005000": (
        "E_ADS_BAD_PATHNAME",
        "An invalid ADSI pathname was passed",
        ProgrammingError,
    ),
    "0x80005001": (
        "E_ADS_INVALID_DOMAIN_OBJECT",
        "An unknown ADSI domain object was requested",
        DataError,
    ),
    "0x80005002": (
        "E_ADS_INVALID_USER_OBJECT",
        "An unknown ADSI user object was requested",
        DataError,
    ),
    "0x80005003": (
        "E_ADS_INVALID_COMPUTER_OBJECT",
        "An unknown ADSI computer object was requested",
        DataError,
    ),
    "0x80005004": (
        "E_ADS_UNKNOWN_OBJECT",
        "An unknown ADSI object was requested",
        DataError,
    ),
    "0x80005005": (
        "E_ADS_PROPERTY_NOT_SET",
        "The specified ADSI property was not set",
        InternalError,
    ),
    "0x80005006": (
        "E_ADS_PROPERTY_NOT_SUPPORTED",
        "The specified ADSI property is not supported",
        ProgrammingError,
    ),
    "0x80005007": (
        "_ADS_PROPERTY_INVALID",
        "The specified ADSI property is invalid",
        IntegrityError,
    ),
    "0x80005008": (
        "E_ADS_BAD_PARAMETER",
        "One or more input parameters are invalid",
        IntegrityError,
    ),
    "0x80005009": (
        "E_ADS_OBJECT_UNBOUND",
        "The specified ADSI object is not bound to a remote resource",
        InternalError,
    ),
    "0x8000500A": (
        "E_ADS_PROPERTY_NOT_MODIFIED",
        "The specified ADSI object has not been modified",
        IntegrityError,
    ),
    "0x8000500C": (
        "E_ADS_CANT_CONVERT_DATATYPE",
        "The data type cannot be converted to/from a native DS data type",
        DataError,
    ),
    "0x8000500D": (
        "E_ADS_PROPERTY_NOT_FOUND",
        "The property cannot be found in the cache",
        OperationalError,
    ),
    "0x8000500E": ("E_ADS_OBJECT_EXISTS", "The ADSI object exists", InternalError),
    "0x8000500F": (
        "E_ADS_SCHEMA_VIOLATION",
        "The attempted action violates the directory service schema rules",
        IntegrityError,
    ),
    "0x80005010": (
        "E_ADS_COLUMN_NOT_SET",
        "The specified column in the ADSI was not set",
        InternalError,
    ),
    "0x80005014": (
        "E_ADS_INVALID_FILTER",
        "The specified search filter is invalid",
        ProgrammingError,
    ),
}
"""Error codes for the Active Directory API. Each error is composed of (error_code, error_message, exception_class)."""


def get_com_exception(error_code: int) -> Tuple[str, str, Exception]:
    """
    Get the exception class and message from the error code.
    """

    try:
        return AD_EXCEPTIONS[hex(error_code % 2**32).strip("L")]
    except KeyError:
        return ("Unknown Error", "An unknown error occurred.", DatabaseError)
