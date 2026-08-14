.PHONY: lint-fix type start

lint-fix:
	ruff check --fix
	ruff format

type:
	mypy .


start:
	python src/main.py
