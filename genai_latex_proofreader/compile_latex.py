from pathlib import Path
from typing import Callable

from genai_latex_proofreader.latex_interface.data_model import LatexDocument

from .latex_interface.data_model import to_latex
from .utils.run_commands import CommandResult, run_commands


def _compile_commands(path: Path) -> list[str]:
    """
    Return Latex commands to compile a LaTeX document (including any bibliography)

    Input path is the relative path to the main LaTeX file after files have been
    copied to the temp directory.
    """
    return [
        f"pdflatex -interaction=nonstopmode {path}",
        f"bibtex {path.with_suffix('.aux')} || true",
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


def compile_latex_doc(
    doc: LatexDocument,
    doc_path: Path,
    compile_commands: Callable[[Path], list[str]] = _compile_commands,
) -> list[CommandResult]:
    return compile_latex(
        files={
            **doc.supporting_files,
            doc_path: to_latex(doc).encode("utf-8"),
        },
        main_file=doc_path,
        compile_commands=compile_commands,
    )
