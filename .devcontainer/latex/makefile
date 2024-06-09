build:
	docker --version
	docker compose build genai-latex-proofreader-service

in-docker/run-make:
	docker compose run \
	    --rm \
	    --tty \
	    --entrypoint "make" \
	    genai-latex-proofreader-service \
	    ${MAKE_TASK}