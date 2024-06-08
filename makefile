.PHONE: *
SHELL := /bin/bash

run-mypy:
	@date
	@mypy .

run-unit-tests:
	@date
	@pytest tests/unit

run-integration-tests:
	@# Run integration tests that require access to a GenAI API
	@date
	@pytest tests/integration

watch-run-unit-tests:
	@# Run tests whenever a Python file is updated, or one press Space in terminal
	@(find . | grep ".py" | entr ${MAKE} run-unit-tests)

