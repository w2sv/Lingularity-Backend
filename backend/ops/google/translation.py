import socket

from googletrans import LANGUAGES, Translator

from backend.ops.google import GoogleOp


socket.setdefaulttimeout(15 * 60)


class GoogleTranslator(GoogleOp):
    _translator = Translator()
    _LANGUAGE_2_IDENTIFIER = {v.title(): k for k, v in LANGUAGES.items()}

    def translate(self, text: str, dest: str, src: str) -> str:
        """ Args:
                text: to be translated
                src: titular source language
                dest: titular destination language """

        return self._translator.translate(text, *map(self._get_identifier, [dest, src])).text
