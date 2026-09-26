.DEFAULT_GOAL := install

install:
	@mise install
	@pre-commit install
	@uv sync

check:
	@uv run tox -e lint
	@pre-commit run --all-files

update:
	@uv lock --upgrade
	@uv sync
	@pre-commit autoupdate

update-tooling:
	@copier update --trust --skip-answered --answers-file .copier-python-poetry-answers.yml

test:
	# Running tests
	@uv run tox
