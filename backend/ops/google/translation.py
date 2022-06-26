# import socket
#
# from googletrans import LANGUAGES, Translator
#
# from backend.ops.google import GoogleOperationClient
#
#
# socket.setdefaulttimeout(15 * 60)
#
# _translator = Translator()
#
#
# class GoogleTranslator(GoogleOperationClient):
#     def __init__(self):
#         super().__init__(_LANGUAGE_2_IETF_TAG={v.title(): k for k, v in LANGUAGES.items()})
#
#     def translate(self, string: str, dest: str, src: str) -> str:
#         """ Args:
#                 string: to be translated
#                 src: titular source language
#                 dest: titular destination language """
#
#         return _translator.translate(string, *map(self._get_identifier, [dest, src])).string
