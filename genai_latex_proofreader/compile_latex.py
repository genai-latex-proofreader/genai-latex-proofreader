from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .utils.io import read_directory, write_directory
from .utils.run_commands import CommandResult, run_commands


def _compile_commands(path: Path) -> list[str]:
    """
    Return Latex commands to compile a LaTeX document (including any bibliography)

    Input path is the relative path to the main LaTeX file after files have been
    copied to the temp directory.
    """
    return [
        f"pdflatex -interaction=nonstopmode {path}",
        f"bibtex {path.with_suffix('.aux')}",
        f"pdflatex -interaction=nonstopmode {path}",
        f"pdflatex -interaction=nonstopmode {path}",
    ]


def compile_latex(
    files: dict[Path, bytes],
    main_file: Path,
    compile_commands: Callable[[Path], list[str]] = _compile_commands,
) -> list[CommandResult]:
    """
    Compile a LaTeX document from the provided files.

    Args:
        files: files to create in the temp directory
        main_file: Path to the main LaTeX file

    Returns:
        Output after running the compile commands (return value from run_commands).
    """

    return run_commands(files, compile_commands(main_file))
