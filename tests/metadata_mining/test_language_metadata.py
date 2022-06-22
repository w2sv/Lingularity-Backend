from backend.data_mining.online_data.scraping import sentence_data_download_links
from backend.metadata import language_metadata


def test_download_link_currency():
    for language, link in sentence_data_download_links.scrape().items():
        assert link == language_metadata[language]['sentenceDataDownloadLinks']['tatoebaProject']
