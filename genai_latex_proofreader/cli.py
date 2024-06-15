from argparse import ArgumentParser
from pathlib import Path

from .compile_latex import compile_latex
from .latex_interface.data_model import to_summary
from .latex_interface.parser import parse_from_latex
from .utils.io import read_directory


def args():
    parser = ArgumentParser()
    parser.add_argument(
        "--input_latex_path",
        required=True,
        type=Path,
    )
    return parser.parse_args()


if __name__ == "__main__":
    print(f"--- genai-latex-proofreader ---")
    input_directory: Path = args().input_latex_path.parent
    main_file: Path = args().input_latex_path.relative_to(input_directory)

    files_in_scope = read_directory(input_directory)
    print("Files in scope")
    for file, content in files_in_scope.items():
        print(f"{file}   ({len(content)} bytes)")

    # Check that we can parse the main Latex file
    output = compile_latex(files_in_scope, main_file)

    # Check that input Latex document compiles successfully
    if output[-1].returncode == 0:
        print(f"Input LaTeX document {main_file} compiled successfully [OK]")
    else:
        raise Exception(
            f"Input LaTeX document {main_file} did not compile successfully [FAIL]:\n"
            f" - returncode: {output[-1].returncode}\n"
            f" - stdout: {output[-1].stdout}\n"
            f" - stderr: {output[-1].stderr}\n"
        )

    doc = parse_from_latex(files_in_scope[main_file].decode("utf-8"))
    print(f"Input LaTeX document {main_file} parses successfully [OK]")
    print("--- Summary ---")
    print(to_summary(doc))
