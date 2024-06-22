"""
Test e2e proofreading of a scientific paper with access to GenAI API
"""

from pathlib import Path

from genai_latex_proofreader.compile_latex import compile_latex_doc
from genai_latex_proofreader.genai_interface.anthropic import GenAIClient
from genai_latex_proofreader.genai_proofreader.runner import proofread_paper
from genai_latex_proofreader.latex_interface.data_model import to_latex
from genai_latex_proofreader.latex_interface.parser import parse_from_latex
from genai_latex_proofreader.utils.io import write_directory

input_latex: str = r"""\documentclass{article}

\begin{document}
\title{Sample Latex Document}
\maketitle

\section{Introduction}
\label{sec:intro}
Hello world. This is introduction to a scientific paper.

\section{Proof of main result}
Because A and B, we have C. This is the main result of the paper.

\end{document}"""


def test_e2e_proofread_empty_paper(tmp_path: Path):

    # For debugging it can be helpful to inspect logged qe
    # tmp_path = Path("tests-e2e-genai-logs")

    client = GenAIClient(tmp_path, max_tokens=2000)

    doc = parse_from_latex(input_latex)

    (tmp_path / "input.tex").write_text(to_latex(doc))

    report = proofread_paper(client, doc)

    # color package should be loaded in the report
    assert r"\usepackage{color}" in to_latex(report)
    (tmp_path / "output.tex").write_text(to_latex(report))

    # The output document contains proofreading comments
    assert r"\typeout{START: " in to_latex(report)
    assert r"\typeout{END: " in to_latex(report)

    # The output document should compile successfully
    compiled = compile_latex_doc(report, Path("main.tex"))[-1]
    write_directory(compiled.output_files, tmp_path / "output")

    assert compiled.returncode == 0
