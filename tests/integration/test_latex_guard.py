"""
Test fixing invalid latex code using GenAI
"""

from pathlib import Path

import pytest

from genai_latex_proofreader.compile_latex import compile_latex_doc
from genai_latex_proofreader.genai_interface.anthropic import GenAIClient
from genai_latex_proofreader.genai_proofreader.latex_guard import LatexGuard
from genai_latex_proofreader.latex_interface.data_model import to_latex
from genai_latex_proofreader.latex_interface.parser import parse_from_latex
from genai_latex_proofreader.proofread_comments.add_comments import add_comments

input_latex = r"""\documentclass{article}

\begin{document}
\title{Sample Latex Document}
\maketitle

\section{Introduction}
\label{sec:intro}
Hello world.
\end{document}"""


@pytest.mark.parametrize(
    "proofreading_comment",
    [
        r"\CommandDoesNotExist{....}",
        r"A wrong formula $\frac{1}",
        r"\begin{itemize}\item boo!",
        r"\begin{itemize}\item one item \item item two \begin{itemize}\item Item three",
        r"\end{itemize}\item boo!",
    ],
)
def test_latex_guard(proofreading_comment: str):
    client = GenAIClient(Path("latex-proofreader-logs"), max_tokens=2000)
    doc = parse_from_latex(input_latex)
    section_ref = list(doc.content_dict.keys())[-1]

    latex_guard = LatexGuard(client, doc)
    _, new_comment = latex_guard((section_ref, proofreading_comment))

    doc_modified = add_comments(doc, section_ref, [new_comment])

    run = compile_latex_doc(doc_modified, Path("main.tex"))[-1]
    if run.returncode != 0:
        print(to_latex(doc_modified))
        print(run.stdout)
        assert False
