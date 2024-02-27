.PHONY: help clean dist test

.DEFAULT_GOAL := help

help: 	## Display this help.
	@echo "Please use \`make <target>' where <target> is one of:"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: 	## Clean the repo.
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache htmlcov

test:   ## Test the scripts.
	act -q && black -q --diff --check . && mypy . && pylama && pylint -E --recursive=y . && \
	pytest -q --cache-clear --no-header --no-summary -c missing --cov --cov-branch --cov-report=html --pylint --pylama \
	&& ruff . && pre-commit run --all-files
