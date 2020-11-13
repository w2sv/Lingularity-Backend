# type: ignore

""" Refactored version of the google text-to-speech token generation algorithm by Boudewijn26
to be found at https://github.com/Boudewijn26/gTTS-token/blob/master/gtts_token/gtts_token.py """

from typing import Optional
import calendar
import math
import time
import requests
import re

from backend.logging import log


_SALT_1 = "+-a^+6"
_SALT_2 = "+-3^+b+-f"


_MAX_TOKEN_KEY_RETRIEVAL_RETRIES = 10


def _retrieve_token_key(retry=0) -> str:
    response = requests.get("https://translate.google.com/")
    tkk_expr = re.search("(tkk:.*?),", response.text)

    if tkk_expr is None:
        if retry < _MAX_TOKEN_KEY_RETRIEVAL_RETRIES:
            log(f'Erroneous Google tts token key retrieval after retry {retry}')

            return _retrieve_token_key(retry=retry + 1)
        else:
            raise ValueError(f"Couldn't retrieve google text-to-speech token key after {_MAX_TOKEN_KEY_RETRIEVAL_RETRIES} retries")

    tkk_expr = tkk_expr.group(1)

    try:
        # Grab the token directly if already generated by function call
        result = re.search("\d{6}\.[0-9]+", tkk_expr).group(0)
    except AttributeError:
        # Generate the token using algorithm
        timestamp = calendar.timegm(time.gmtime())
        hours = int(math.floor(timestamp / 3600))
        a = re.search("a\\\\x3d(-?\d+);", tkk_expr).group(1)
        b = re.search("b\\\\x3d(-?\d+);", tkk_expr).group(1)

        result = str(hours) + "." + str(int(a) + int(b))

    return result


_token_key: Optional[str] = None


def _get_token_key() -> str:
    global _token_key
    if _token_key is None:
        _token_key = _retrieve_token_key()
    return _token_key


def calculate(text: str) -> str:
    [first_seed, second_seed] = _get_token_key().split(".")

    try:
        d = bytearray(text.encode('UTF-8'))
    except UnicodeDecodeError:
        # This will probably only occur when d is actually a str containing UTF-8 chars, which means we don't need
        # to encode.
        d = bytearray(text)

    a = int(first_seed)
    for value in d:
        a += value
        a = _work_token(a, _SALT_1)
    a = _work_token(a, _SALT_2)
    a ^= int(second_seed)
    if 0 > a:
        a = (a & 2147483647) + 2147483648
    a %= 1E6
    a = int(a)
    return str(a) + "." + str(a ^ int(first_seed))


def _rshift(val: int, n: int) -> int:
    return val >> n if val >= 0 else (val + 0x100000000) >> n


def _work_token(a: int, seed: str) -> int:
    for i in range(0, len(seed) - 2, 3):
        char = seed[i + 2]
        d = ord(char[0]) - 87 if char >= "a" else int(char)
        d = _rshift(a, d) if seed[i + 1] == "+" else a << d
        a = a + d & 4294967295 if seed[i] == "+" else a ^ d
    return a