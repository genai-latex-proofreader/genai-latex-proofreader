def format_report(
    report: str,
    review_comment_header: str,
    label: str,
) -> str:
    wrapped_report = (
        r"""

\typeout{START: <REVIEW_LABEL>}

\textcolor[RGB]{126,126,126}{\rule{\linewidth}{1pt}}

{\tiny
    {\color{red}
        <REVIEW_HEADER>
        <REPORT>
    }
}

\textcolor[RGB]{126,126,126}{\rule{\linewidth}{1pt}}

\typeout{END: <REVIEW_LABEL>}

""".replace(
            "<REVIEW_LABEL>", label
        )
        # role, task, what was provided for review
        .replace("<REVIEW_HEADER>", review_comment_header)
        # -
        .replace("<REPORT>", report)
    )

    return wrapped_report


def project_plug() -> str:
    """
    Insert link to GenAI-Latex-Proofreader project
    """
    return format_report(
        report="",
        review_comment_header=(
            r"This document has been proofread using \textbf{GenAI-Latex-Proofreader}: \\"
            r"See: https://github.com/genai-latex-proofreader/genai-latex-proofreader \\"
        ),
        label="project-plug",
    )


def make_review_comment_header(
    role: str, task: str, content_provided_for_review: str
) -> str:
    return (
        (
            r"\textbf{Role:} \emph{<ROLE>} \\"
            r"\textbf{Task:} \emph{<TASK>} \\"
            r"\textbf{Content provided for review:} \emph{<CONTENT_PROVIDED_FOR_REVIEW>}"
            r"\\ \\"
        )
        .replace("<ROLE>", role)
        .replace("<TASK>", task)
        .replace("<CONTENT_PROVIDED_FOR_REVIEW>", content_provided_for_review)
    )
