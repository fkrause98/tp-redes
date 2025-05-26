.PHONY: type-check env measurements

PYTHON := $(shell which python3)

virtualenv:
	$(PYTHON) -m venv ./virtualenv

deps:
	pip install -r ./requirements.txt

type-check:
	mypy --config-file "./mypy.ini" traceroute.py

lint:
	ruff check

measurements:
	sudo ./test.sh
