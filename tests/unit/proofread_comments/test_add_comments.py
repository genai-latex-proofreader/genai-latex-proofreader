import pytest

from genai_latex_proofreader.latex_interface.data_model import to_latex
from genai_latex_proofreader.latex_interface.parser import parse_from_latex
from genai_latex_proofreader.proofread_comments.add_comments import add_comments
from genai_latex_proofreader.proofread_comments.data_model import (
    SectionComment,
    SectionRef,
)


def test_add_comments_fails_if_reference_is_invalid():
    input_latex = r"""\documentclass{article}

\begin{document}
\maketitle

\section{Introduction}
\label{sec:intro}
An introduction.

\bibliography{refs}
\end{document}"""

    with pytest.raises(Exception):
        add_comments(
            parse_from_latex(input_latex),
            # 'sec:intro' is not in Appendix
            {SectionRef(True, "sec:intro"): SectionComment(["..."])},
        )

    with pytest.raises(Exception):
        add_comments(
            parse_from_latex(input_latex),
            # 'sec:intro2' does not exist
            {SectionRef(False, "sec:intro2"): SectionComment(["..."])},
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

\bibliography{refs}
\end{document}"""

    if add_to_appendix:
        input_latex = input_latex.replace(r"%%%%", r"\appendix")

    proofreading_comment = r"\textbf{This section contains a typo; ir should be it!}"

    modified_latex = to_latex(
        add_comments(
            parse_from_latex(input_latex),
            {
                SectionRef(add_to_appendix, "sec:with:typo"): SectionComment(
                    [proofreading_comment]
                )
            },
        )
    )

    assert proofreading_comment in modified_latex
    assert (
        modified_latex.index(r"\section{Section with a typo}")
        < modified_latex.index(proofreading_comment)
        < modified_latex.index("We are proofreading this section, and ir has a typo.")
    )
