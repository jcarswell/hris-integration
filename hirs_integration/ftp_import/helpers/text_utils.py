from typing import Union
from string import ascii_letters,digits

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
    if isinstance(s,bytes):
        return s.decode('utf-8')
    elif isinstance(s,str):
        return s
    else:
        return str(s)

def clean_phone(s:str) -> int:
    output = []
    for l in s:
        if l in digits:
            output.append(l)
    
    if len(output) == 10:
        return "(%s%s%s) %s%s%s-%s%s%s%s" % tuple(output)
    else:
        return "".join(output)