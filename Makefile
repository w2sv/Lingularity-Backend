SHELL=/bin/bash

# --------------
# Installing
# --------------
install:
	bash os-dependencies/install-linux-dependencies.sh

	rm -rf env
	mamba env create -f environment.yml --prefix ./env

install-spacy-models:
	python -m backend.ops.normalizing.lemmatizing.model_downloading

# --------------
# Mining
# --------------
download-sentence-data:
	python -m backend.ops.data_mining.downloading.sentence_data

create-token-maps:
	python -m backend.trainers.components.mappings.token.create

mine-metadata:
	python -m backend.metadata.mine -Mine

# --------------
# Testing
# --------------
test: mypy pytest doctest  # run with -k flag in order to continue in case of recipe failure

mypy:
	mypy backend/

pytest:
	coverage run -m pytest -vv tests/ --ignore=tests/metadata_mining

doctest:
	python -m pytest -vv --doctest-modules --doctest-continue-on-failure ./backend/

test-metadata-mining:
	pytest -vv tests/metadata_mining

# --------------
# Building
# --------------
wheel:
	rm -rf backend.egg-info
	rm -rf build
	python setup.py bdist_wheel --dist-dir ./dist
