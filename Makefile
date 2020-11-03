SHELL=/bin/bash

# ----------Installation--------------

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
	coverage run -m pytest -vv tests/

doctest:
	python -m pytest -vv --doctest-modules --doctest-continue-on-failure ./backend/

# ----------Mining--------------

mine-metadata:
	python -m backend.metadata.mine -Mine

# -----------Building-------------
wheel:
	python setup.py bdist_wheel --dist-dir ../../dist
