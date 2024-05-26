.PHONE: *
SHELL := /bin/bash

run-pytest:
	@date
	@pytest tests

watch-run-pytest:
	@# Run tests whenever a Python file is updated, or one press Space in terminal
	@(find genai_latex_proofreader tests | grep ".py" | entr ${MAKE} run-pytest)


