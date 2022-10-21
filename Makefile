checkfiles = vpsmon/ tests/ conftest.py
py_warn = PYTHONDEVMODE=1

style:
	@isort -src $(checkfiles)
	@black $(checkfiles)

check:
	@black --check $(checkfiles)
	@ruff $(checkfiles)
	@mypy $(checkfiles)

test:
	$(py_warn) pytest

ci: check test
