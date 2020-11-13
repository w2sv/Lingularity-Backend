from backend.utils.module_interfacing import abstractmodulemethod

from . import (
    countries,
    demonym,
    forenames,
    sentence_data_download_links
)


@abstractmodulemethod(ignore_modules=['_utils'])
def scrape():
    pass
