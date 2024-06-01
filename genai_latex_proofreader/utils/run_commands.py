"""
Helper functions to to run commands in a subprocess, and collect results
(ie., files, stdout, errout and error codes).
"""

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str
    returncode: int
    output_files: dict[Path, bytes]


def _execute_command(command: str, cwd: Path) -> CommandResult:
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, cwd=cwd, check=False
    )

    # Recursively get all files under cwd
    output_files = {}
    for file_path in cwd.glob("**/*"):
        if file_path.is_file():
            output_files[file_path.relative_to(cwd)] = file_path.read_bytes()

    command_result = CommandResult(
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
        returncode=result.returncode,
        output_files=output_files,
    )
    if command_result.stderr != "" and command_result.returncode == 0:
        print(
            f"Warning: "
            f"return code is 0, but stderr is not empty ({command_result.stderr})."
        )

    return command_result


def run_commands(files: dict[Path, bytes], commands: list[str]) -> list[CommandResult]:
    """
    Run a list of commands in a temp directory populated with provided files. After
    the commands are run, outputs (stdout, stderr, return code) are returned.
    Command execution stops after first command failure (return code != 0).

    Args:
        files: files to create in the temp directory
        commands: list of commands to run.

    Returns:
        List of CommandResult objects, one for each command that has completed,
        either successfully (return code=0) or not (return code !=0).
        Execution stops on the first failure (return code != 0), so the list may
        be shorter than the input list of commands.

        This means:
          - Only the last element in the return value may have a return code != 0.
          - Eg., if the first command fails, we only return one CommandResult object.
          - All commands ran successfully if the return code of the last element is 0.
    """
    if len(commands) == 0:
        raise Exception("No compile commands provided")

    with tempfile.TemporaryDirectory() as _temp_dir:
        temp_path: Path = Path(_temp_dir)

        for file_path, content in files.items():
            if isinstance(content, bytes):
                (temp_path / file_path).write_bytes(content)
            else:
                raise Exception(f"Unknown type of content {type(content)}")

        def _get_results():
            for command in commands:
                command_result = _execute_command(command, temp_path)

                yield command_result
                if command_result.returncode != 0:
                    break

        return list(_get_results())
