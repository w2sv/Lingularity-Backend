SHELL=/bin/bash

# --------------
# Installing
# --------------
install: _install install-spacy-models

_install:
	poetry install

install-spacy-models:
	poetry run install-spacy-models

# --------------
# Testing
# --------------
test: mypy pytest doctest coverage-report  # run with -k flag in order to continue in case of recipe failure

mypy:
	mypy backend/

pytest:
	coverage run -m pytest -vv tests/ --randomly-seed=69

coverage-report:
	coverage xml
	coverage report

doctest:
	python -m pytest \
				-vv \
				--doctest-modules \
				--doctest-continue-on-failure ./backend/

##############
# Publishing #
##############

publish-patched: test patch-version _publish

patch-version:
	poetry version patch

_publish:
	poetry publish --build
