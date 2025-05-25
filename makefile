.PHONY: type-check env

PYTHON := $(shell command -v python3 || command -v python)

check-python:
	@test -n "$(PYTHON)" || (echo "Error: No Python executable found" && exit 1)

virtualenv:
	$(PYTHON) -m venv ./virtualenv

deps:
	pip install -r ./requirements.txt

type-check:
	mypy --config-file "./mypy.ini" traceroute.py

lint:
	ruff check
