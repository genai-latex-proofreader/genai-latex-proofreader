def format_report(
    report: str,
    review_header: str,
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
        .replace("<REVIEW_HEADER>", review_header)
        # -
        .replace("<REPORT>", report)
    )

    return wrapped_report
