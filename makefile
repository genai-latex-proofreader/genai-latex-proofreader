.PHONE: *
SHELL := /bin/bash

run-mypy:
	@date
	@mypy .

run-pytest:
	@date
	@pytest tests

watch-run-pytest:
	@# Run tests whenever a Python file is updated, or one press Space in terminal
	@(find . | grep ".py" | entr ${MAKE} run-pytest)

