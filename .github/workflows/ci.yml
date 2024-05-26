name: "ci: Test python code"

on:
  workflow_dispatch:

  push:
    branches:
      - main

  pull_request:
    branches:
      - main
    paths-ignore:
      - README.md

permissions:
  contents: read

jobs:
  ci-run-tests:
    runs-on: ubuntu-24.04
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v3
        with:
          persist-credentials: false

      - name: Build docker images
        run: |
          (cd .devcontainer/latex; make build)

      - name: Check static code checking (mypy)
        run: |
          (cd .devcontainer/latex; make in-docker/run-make MAKE_TASK="run-mypy")

      - name: Check tests using pytest
        run: |
          (cd .devcontainer/latex; make in-docker/run-make MAKE_TASK="run-pytest")
