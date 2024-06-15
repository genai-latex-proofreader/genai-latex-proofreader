import pytest

from genai_latex_proofreader.latex_interface.data_model import (
    PreSectionRef,
    SectionRef,
    to_latex,
)
from genai_latex_proofreader.latex_interface.parser import parse_from_latex
from genai_latex_proofreader.proofread_comments.add_comments import add_comments


def test_add_comments_fails_if_reference_is_invalid():
    input_latex = r"""\documentclass{article}

\begin{document}
\maketitle

\section{Introduction}
\label{sec:intro}
An introduction.
\end{document}"""

    with pytest.raises(Exception):
        add_comments(
            parse_from_latex(input_latex),
            SectionRef(
                in_appendix=True,  # <- Introduction is not in appendix
                title="Introduction",
                label="sec:intro",
                generated_label="xx",
            ),
            ["..."],
        )


@pytest.mark.parametrize("add_to_appendix", [True, False])
def test_add_comments_to_appendix(add_to_appendix: bool):
    input_latex = r"""\documentclass{article}

\begin{document}
\maketitle

\section{Introduction}
\label{sec:intro}
An introduction.

%%%%

\section{Section with a typo}
\label{sec:with:typo}
We are proofreading this section, and ir has a typo.
\end{document}"""

    if add_to_appendix:
        input_latex = input_latex.replace(r"%%%%", r"\appendix")

    proofreading_comment = r"\textbf{This section contains a typo; ir should be it!}"

    doc = parse_from_latex(input_latex)

    # add comment to last section in entire document
    ref_to_section_with_typo = list(doc.content_dict.keys())[-1]

    modified_latex = to_latex(
        add_comments(doc, ref_to_section_with_typo, [proofreading_comment])
    )

    assert proofreading_comment in modified_latex
    assert (
        modified_latex.index(r"\section{Section with a typo}")
        < modified_latex.index(proofreading_comment)
        < modified_latex.index("We are proofreading this section, and ir has a typo.")
    )
