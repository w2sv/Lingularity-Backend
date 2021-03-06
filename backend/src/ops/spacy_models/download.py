from spacy import cli

from backend.src.ops.spacy_models import LANGUAGE_2_MODEL_PARAMETERS, model_name


def download_models():
    for language in LANGUAGE_2_MODEL_PARAMETERS.keys():
        cli.download(model_name(language=language))


def download_model(language: str):
    cli.download(model_name(language=language))