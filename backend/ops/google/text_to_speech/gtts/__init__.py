""" Optimized version of https://github.com/pndurette/gTTS/blob/master/gtts/tts.py """

import requests
from six.moves import urllib
import urllib3

from backend.ops.google.text_to_speech.gtts import _token


_GOOGLE_TTS_HEADERS = {
    "Referer": "http://translate.google.com/",
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/47.0.2526.106 Safari/537.36"
}


def get_audio(text: str, language_identifier: str, save_path: str):
    response = _request_audio(text=text, language_identifier=language_identifier)
    _write_data_to_file(response, file_path=save_path)


def _request_audio(text: str, language_identifier: str) -> requests.Response:
    # When disabling ssl verify in requests (for proxies and firewalls),
    # urllib3 prints an insecure warning on stdout. We disable that.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    with requests.Session() as session:
        response = session.send(
            request=_prepare_request(text=text, language_identifier=language_identifier),
            proxies=urllib.request.getproxies(),
            verify=False
        )

    response.raise_for_status()
    return response


def _prepare_request(text: str, language_identifier: str) -> requests.PreparedRequest:
    """Created the TTS API the request(s) without sending them.

    Returns:
        list: ``requests.PreparedRequests_``. <https://2.python-requests.org/en/master/api/#requests.PreparedRequest>`_``.
    """

    URL = f"https://translate.google.com/translate_tts"
    token = _token.calculate(text=text)  # type: ignore

    payload = {
        'ie': 'UTF-8',
        'q': text,
        'tl': language_identifier,
        'ttsspeed': 1.0,
        'client': 'tw-ob',
        'textlen': len(text),
        'tk': token
    }

    return requests.Request(
        method='GET',
        url=URL,
        params=payload,
        headers=_GOOGLE_TTS_HEADERS
    ).prepare()


def _write_data_to_file(response: requests.Response, file_path: str):
    with open(file_path, 'wb') as write_file:
        try:
            for chunk in response.iter_content(chunk_size=1024):
                write_file.write(chunk)
        except (AttributeError, TypeError):
            raise TypeError(f"Passed file_path is either not a file-like object or does not take bytes")
