SHELL=/bin/bash

# ----------Installing--------------

install:
	bash os-dependencies/base.sh

	rm -rf env
	conda env create -f environment.yml --prefix ./env

download-spacy-models:
	python -m backend.utils.spacy

# ----------Testing----------

test: mypy pytest doctest  # run with -k flag in order to continue in case of recipe failure

mypy:
	mypy backend/

pytest:
	coverage run -m pytest -vv tests/ --ignore=tests/metadata_mining

doctest:
	python -m pytest -vv --doctest-modules --doctest-continue-on-failure ./backend/

test-metadata-mining:
	pytest -vv tests/metadata_mining

# ----------Mining--------------

mine-metadata:
	python -m backend.metadata.mine -Mine

# -----------Building-------------
wheel:
	rm -rf backend.egg-info
	rm -rf build
	python setup.py bdist_wheel --dist-dir ../dist
