from pathlib import Path

import pytest

from genai_latex_proofreader.command_runner import CommandResult, run_commands


def test_run_commands_all_success():
    assert run_commands({}, ["echo '123'", "echo '456'"]) == [
        CommandResult(stdout="123", stderr="", returncode=0),
        CommandResult(stdout="456", stderr="", returncode=0),
    ]


def test_run_commands_execution_stops_on_first_failure():
    results = run_commands(
        {
            Path("file1.txt"): "Hello, World!",
            Path("file2.txt"): bytes([1, 2, 3]),
        },
        [
            "cat file1.txt",
            "cat file2.txt",
            "cat file-does-not-exist.txt",
            "echo '123'",  # command not executed since execution stops on first failure
        ],
    )

    assert results == [
        CommandResult(stdout="Hello, World!", stderr="", returncode=0),
        CommandResult(stdout="\x01\x02\x03", stderr="", returncode=0),
        CommandResult(
            stdout="",
            stderr="cat: file-does-not-exist.txt: No such file or directory",
            returncode=1,
        ),
    ]

    # the files should not be created in the current directory
    with pytest.raises(FileNotFoundError):
        Path("file1.txt").read_text()


def test_run_commands_fail_with_no_commands():
    with pytest.raises(Exception) as e:
        run_commands(files={}, commands=[])
    assert str(e.value) == "No compile commands provided"
