from typing import Union

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