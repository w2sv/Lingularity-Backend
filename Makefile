SHELL=/bin/bash

# --------------
# Installing
# --------------
install:
	rm -rf env
	mamba env create -f environment.yml --prefix ./env

install-spacy-models:
	python -m model_downloading

# --------------
# Testing
# --------------
test: mypy pytest doctest  # run with -k flag in order to continue in case of recipe failure

mypy:
	mypy backend/

pytest:
	coverage run -m pytest -vv tests/
	coverage report

doctest:
	python -m pytest -vv --doctest-modules --doctest-continue-on-failure ./backend/

# --------------
# Building
# --------------
wheel:
	rm -rf backend.egg-info
	rm -rf build
	python setup.py bdist_wheel --dist-dir ./dist
