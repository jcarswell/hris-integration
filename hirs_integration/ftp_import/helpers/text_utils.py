from datetime import datetime
from typing import Union
from string import ascii_letters,digits
from fuzzywuzzy import fuzz
from django.utils.timezone import make_aware,is_aware

def int_or_str(val:str) -> Union[int,str]:
    """
    Converts a giving string into an int or returns the original string

    Args:
        val (str): a string to try and transform

    Raises:
        ValueError: provided value is not an string or int

    Returns:
        Union[int,str]: the transformed value
    """
    if type(val) not in [int,str]:
        raise ValueError("value is not an int or str")
    try:
        return int(val)
    except ValueError:
        return val

def safe(val:str) -> str:
    """Cleans a string for safe parsing in the database and function. Helps ensure
    that the source value is always future matchable.

    Args:
        val (str): source string

    Returns:
        str: cleaned string stripped of all special characters except - or _
    """
    output = []
    for l in val:
        if l == ' ':
            output.append('_')
        elif l not in ascii_letters+digits+'_':
            output.append('-')
        else:
            output.append(l.lower())

    return "".join(output)

def decode(s) -> str:
    """Decodes a bytes object to a string

    Args:
        s (bytes|str): source string

    Returns:
        str: decoded string value
    """
    if isinstance(s,bytes):
        return s.decode('utf-8')
    elif isinstance(s,str):
        return s
    else:
        return str(s)

def clean_phone(s:str,pretty=True) -> int:
    """Pretty format source phone number and strips non-numeric characters

    Args:
        s (str): source phone number
        pretty: return 10 digit phone number as (xxx) xxx-xxxx

    Returns:
        int: cleaned and formatted phone number
    """
    output = []
    for l in s:
        if l in digits:
            output.append(l)

    if len(output) == 10 and pretty:
        return "(%s%s%s) %s%s%s-%s%s%s%s" % tuple(output)
    else:
        return "".join(output)

def fuzz_name(csv_fname:str,csv_lname:str,emp_fname:str,emp_lname:str,match_pcent:int =80) -> tuple[bool,int]:
    """Compares and employees name and scores it on likely hood of match. Returns true if the match 
    percentage is above [default] 80%.

    Args:
        csv_fname (str): source firstname
        csv_lname (str): source lastname
        emp_fname (str): test firstname
        emp_lname (str): test lastname
        match_pcent (int, optional): Define the matching percentage value. Defaults to 80.

    Returns:
        tuple[bool,int]: If a potential match was found and what matching percentage was.
    """

    ratios = (fuzz.token_sort_ratio(csv_fname,emp_fname) +
             fuzz.token_sort_ratio(csv_lname,emp_lname) +
             fuzz.partial_ratio(f"{csv_fname} {csv_lname}".lower(),f"{emp_fname} {emp_lname}".lower()))

    if ratios/3 >= float(match_pcent):
        return True,int(round(match_pcent,0))
    else:
        return False,int(round(match_pcent,0))

def parse_date(date_str:str) -> datetime:
    from .config import CAT_CSV,CSV_DATE_FMT,Config
    setting = Config()
    setting.get(CAT_CSV,CSV_DATE_FMT)
    dt = datetime.strptime(date_str,setting.value)
    if not is_aware(dt):
        dt = make_aware(dt)

    return dt