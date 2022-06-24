SHELL=/bin/bash

# --------------
# Installing
# --------------
install-spacy-models:
	python -m model_downloading

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
	python -m pytest -vv \
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
