.PHONE: *
SHELL := /bin/bash


# --- Static code analysis ---

run-mypy:
	@date
	@mypy .

run-unit-tests:
	@date
	@pytest tests/unit

watch-run-unit-tests:
	@# Run tests whenever a Python file is updated, or one press Space in terminal
	@(find . | grep ".py" | entr ${MAKE} run-unit-tests)


# --- tasks that require access to GenAI API ---

run-integration-tests:
	@# Run integration tests that require access to a GenAI API
	@date
	@pytest tests/integration

run-e2e-test-proofread-empty-paper:
	@echo "--- Running end-to-end test: proofread empty paper ---"
	@mkdir -p test-proofread-empty-paper/input
	@python3 -m genai_latex_proofreader.cli \
	     --input_latex_path       tests/integration/assets/empty_paper.tex \
	     --output_report_filepath test-proofread-empty-paper/report.tex

	@echo "--- List of generated files ---"
	@find test-proofread-empty-paper

run-e2e-test-proofread-example-paper:
	@# Process an example paper:
	@#
	@#    https://arxiv.org/abs/1108.4207
	@#    Non-dissipative electromagnetic medium with a double light cone
	@#    Matias F. Dahl
	@#    https://doi.org/10.1016/j.aop.2012.11.005
	@#
	@mkdir paper
	@curl https://arxiv.org/e-print/1108.4207 | \
	    tar -xvzf - --directory=paper
	@python3 -m genai_latex_proofreader.cli \
	    --input_latex_path paper/arxiv-1-frame.tex \
	    --output_report_filepath proofreading-report/report.tex

