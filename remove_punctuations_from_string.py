import string
from typing import Optional, Iterable, Union

delete_dict = {sp_character: '' for sp_character in string.punctuation}
PUNCT_TABLE = str.maketrans(delete_dict)
output = []

def strip_punctuation(s: str,exclude_chars: Optional[Union[str, Iterable]] = None) -> str:
    """
    Remove punctuation and spaces from a string.
    If `exclude_chars` is passed, these  will not be removed from the string.
    """
    punct_table = PUNCT_TABLE.copy()
    if exclude_chars:
        for char in exclude_chars:
            punct_table.pop(ord(char), None)
    return s.translate(punct_table)

def clean_keys(obj):
    return {strip_punctuation(k): v for k, v in obj}


print(strip_punctuation("Hello! World#"))