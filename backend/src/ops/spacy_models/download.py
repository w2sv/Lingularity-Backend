from spacy import cli

from backend.src.ops.spacy_models import LANGUAGE_2_MODEL_IDENTIFIERS, model_name


def download_models():
    for language in LANGUAGE_2_MODEL_IDENTIFIERS.keys():
        cli.download(model_name(language=language))