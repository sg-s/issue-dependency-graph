.PHONY: test coverage-report bump-version jupyter

jupyter:
	@echo "Installing kernel <issue_deps> in jupyter"
	-yes | jupyter kernelspec uninstall issue_deps
	poetry run python -m ipykernel install --user --name issue_deps



test:
	poetry run coverage run -m pytest -sx --failed-first
	-rm coverage.svg
	poetry run coverage-badge -o coverage.svg

coverage-report: .coverage
	poetry run coverage html --omit="*/test*"
	open htmlcov/index.html

bump-version:
	poetry run bump