import uuid
from typing import Iterable

import pytest

from genai_latex_proofreader.latex_interface.data_model import to_latex
from genai_latex_proofreader.latex_interface.parser import (
    _extract_sections,
    parse_from_latex,
)

TEST_DOC = r"""\documentclass[12pt, a4paper, twoside]{amsart}

\usepackage{mathrsfs}

\parindent = 0cm
\parskip   = .2cm

\title[short-title]{A longer title for the paper}

\begin{document}

\begin{abstract}
My abstract
\end{abstract}

\maketitle

\section{Introduction}
\label{sec:introduction}
Suppose $g$ is a pseudo-Riemann metric on a smooth $4$-manifold $N$.

\section{The main theorem}
\label{sec:main:theorem}
Some more text

\section{Conclusions}
\label{sec:conclusions}
\section{More conclusions}
\label{sec:more:conclusions}

\appendix

Appendix intro

\section{Derivation of main equations}
\label{sec:app1}
Appendix section introduction

\begin{proof}
The result follows since $x^2 + y^2 = 1$
\end{proof}

\bibliography{refs}
\bibliographystyle{amsalpha}

\end{document}"""


def remove_generated_labels(doc: str) -> str:
    return "\n".join(
        line
        for line in doc.split("\n")
        if not r"\label{sec:genai:generated:label" in line
    )


def test_latex_parser_and_conversion_back_to_latex():
    assert TEST_DOC == remove_generated_labels(to_latex(parse_from_latex(TEST_DOC)))


def test_latex_parser_fail_if_duplicate_labels():
    with pytest.raises(Exception):
        parse_from_latex(
            # create latex document with two sections with label "sec:introduction"
            TEST_DOC.replace(r"{sec:main:theorem}", r"{sec:introduction}")
        )


def test_latex_parser_and_conversion_back_to_latex_without_labels():
    # as above, but modify input to have no section labels
    def remove_labels(doc: str) -> str:
        return "\n".join(
            line for line in doc.split("\n") if not line.startswith(r"\label")
        )

    def only_labels(doc: str) -> list[str]:
        return [line for line in doc.split("\n") if line.startswith(r"\label")]

    output: str = to_latex(parse_from_latex(remove_labels(TEST_DOC)))

    assert remove_labels(output) == remove_labels(TEST_DOC)
    assert len(set(only_labels(output))) == 5  # 4 sections + 1 section in appendix


def generate_sections(
    initial_rows: int, nr_sections: int, nr_rows_per_section: int
) -> Iterable[str]:
    def random_lines(nr_lines: int) -> Iterable[str]:
        for _ in range(nr_lines):
            yield f"{uuid.uuid4()}"

    def section_content(nr_rows: int) -> Iterable[str]:
        section_title = f"Section {uuid.uuid4()}"
        yield rf"\section{{{section_title}}}"
        yield from random_lines(nr_rows)
        section_label = f"sec:{uuid.uuid4()}"
        yield rf"\label{{{section_label}}}"
        yield r"\subsection{A subsection}"
        subsection_label = f"sec:{uuid.uuid4()}"
        yield rf"\label{{{subsection_label}}}"
        yield from random_lines(nr_rows)

    yield from random_lines(initial_rows)
    for _ in range(nr_sections):
        yield from section_content(nr_rows_per_section)


def test_parse_section():
    # test internal function _extract_sections for parsing \section{...}

    for pre_section_lines_count in range(3):
        for sections_nr in range(3):
            for nr_rows_per_section in range(3):
                sections_lines = list(
                    generate_sections(
                        pre_section_lines_count,
                        sections_nr,
                        nr_rows_per_section,
                    )
                )

                assert (
                    remove_generated_labels(
                        to_latex(_extract_sections(sections_lines, is_appendix=False))
                    )
                    # -
                    == "\n".join(sections_lines)
                )


def test_parse_whole_latex_document():

    DOC_TOP = r"""\documentclass[12pt, a4paper, twoside]{amsart}

\usepackage{mathrsfs}

\parindent = 0cm
\parskip   = .2cm

\title[short-title]{Long-title}"""

    # \begin{document}

    DOC_ABSTRACT = r"""
\begin{abstract}
My abstract
\end{abstract}"""

    # \maketitle

    # ... sections/content in main document ...

    # \appendix

    # ... sections/content in appendix ...

    DOC_END = r"""\bibliography{refs}
\bibliographystyle{amsalpha}

\end{document}"""

    for pre_section_lines_count in range(3):
        for sections_nr in range(3):
            for nr_rows_per_section in range(3):
                for include_appendix in [True, False]:

                    sections_lines: list[str] = list(
                        generate_sections(
                            pre_section_lines_count,
                            sections_nr,
                            nr_rows_per_section,
                        )
                    )

                    if include_appendix:
                        potential_appendix = [
                            r"\appendix",
                            *(
                                generate_sections(
                                    pre_section_lines_count,
                                    sections_nr,
                                    nr_rows_per_section,
                                )
                            ),
                        ]
                    else:
                        potential_appendix = []

                    latex_doc = "\n".join(
                        [
                            DOC_TOP,
                            r"\begin{document}",
                            DOC_ABSTRACT,
                            r"\maketitle",
                            *sections_lines,
                            *potential_appendix,
                            DOC_END,
                        ]
                    )

                    assert (
                        remove_generated_labels(to_latex(parse_from_latex(latex_doc)))
                        == latex_doc
                    )