from argparse import ArgumentParser
from dataclasses import replace
from pathlib import Path

from .compile_latex import compile_latex, compile_latex_doc
from .genai_proofreader.runner import proofread_paper
from .latex_interface.data_model import LatexDocument, to_summary, write_latex
from .latex_interface.parser import parse_from_latex, parse_latex_from_files
from .utils.io import read_directory, write_directory


def args():
    parser = ArgumentParser()
    parser.add_argument(
        "--input_latex_path",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "--output_report_filepath",
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

    doc = parse_latex_from_files(files_in_scope, main_file)

    # ensure that the color package is included in report
    doc = replace(doc, pre_matter=doc.pre_matter + [r"\usepackage{color}"])

    print(f"Input LaTeX document {main_file} parses successfully [OK]")
    print("--- Summary ---")
    print(to_summary(doc))

    print(" --- Starting proofreading process ---")
    report: LatexDocument = proofread_paper(
        doc, report_output_filepath=args().output_report_filepath
    )

    print(
        f" --- Writing report (and supporting files) to {args().output_report_filepath} ---"
    )
    write_latex(report, args().output_report_filepath)

    print(" --- Compiling report ---")
    output = compile_latex_doc(report, Path(args().output_report_filepath.name))

    write_directory(output[-1].output_files, args().output_report_filepath.parent)

    if output[-1].returncode == 0:
        print(f"Report compiled successfully [OK]")
    else:
        raise Exception(
            f"Final report did not compile successfully [FAIL]:\n"
            f" - returncode: {output[-1].returncode}\n"
            f" - stdout: {output[-1].stdout}\n"
            f" - stderr: {output[-1].stderr}\n"
        )
