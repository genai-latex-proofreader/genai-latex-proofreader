from pathlib import Path
from typing import Tuple

from ..genai_interface.anthropic import GenAIClient
from ..latex_interface.data_model import (
    ContentReferenceBase,
    LatexDocument,
    PreSectionRef,
    SectionRef,
    to_latex,
)
from ..proofread_comments.add_comments import add_comments

SYSTEM_PROMPT: str = (
    r"""You are distinguished expert in the areas of <AREAS_OF_EXPERTICE>, with
extensive experience in proofreading and providing constructive feedback on academic
papers in your field. You are well-known for your meticulous attention to detail and
your ability to provide insightful suggestions to improve the content, structure, and
clarity of scientific papers.

Your input and ideas are highly regarded by your colleagues and students alike, and you
are committed to help authors improve the quality of their work to meet the high
standards of top journals in the field.""".replace(
        "<AREAS_OF_EXPERTICE>",
        "differential geometry, optics, Maxwell's equations, geometric wave propagation and physics",
    )
)


INSTRUCTIONS_PROMPT: str = (
    r"""Your task is to write up a report for an upcoming paper in your
area of expertise.

The material to proofread is provided in the latex_to_proofread-tag below:

<latex_to_proofread>
{LATEX_CONTENT}
</latex_to_proofread>

Please focus on the following aspects:
- Motivation: Ensure that the problem statement is well motivated.
- Correctness: Critically assess the mathematical arguments for accuracy and proper motivation.
- Clarity: Assess whether the ideas are expressed clearly and concisely, suitable for
  a top scientific journal. Raise any ambiguities or inconsistencies.
- Consistency: Check for consistent use of terminology, abbreviations. Ensure that the
  presentation follow standard conventions in the field.
- Completeness: Verify that all necessary details are provided to support the arguments
  and conclusions.
- References: Check appropriate use of references.

Conclude with a summary of the main strengths and weaknesses, and also provide
suggestions for future research directions and/or broader themes that connect to this
work.

Format your proofreading report as follows:
- For each issues that you find, please provide helpful suggestions on how the issue
  can be resolved or improved.
- Please write up all your findings as a Latex-enumerated list following the structure
  as in the <example_proofread_report> tag below. In particular, your review must begin
  with "\begin{enumerate}" (without the quotes).
- Your proofreading report will be copy-pasted into the paper and then compiled.
  Therefore your report must be valid Latex. Eg. do not write "please use the
  \align environment" since this is not valid Latex.
- You can reference existing labels in the paper.

<example_proofread_report>
\begin{enumerate}
\item Issue 1
\item Issue 2
\end{enumerate}
Short summary of findings, and directions to continue the research.
</example_proofread_report>

---

<FOCUS>

The below topics will be covered by other reviewers:
- Formatting, Latex usage.
- Typos, punctuation and grammar.
- US vs UK english.
So disregard any issues you find on these topics.

Your report will be judged on its clarity of expression, thoroughness, and helpfulness.

Take a deep breath. Remember to be thorough and precise in your proofreading.
"""
    # -
    .replace(
        "<PROOFREAD_TASK_SUMMARY>",
        "Your task is to write up a proofreading report for an upcoming paper. This paper is in your area of expertise.",
    )
)


def _wrap_report(report: str, review_header: str, label: str) -> str:
    # TODO: if latex does not compile, generate error
    return (
        r"""

\typeout{START OF <REVIEW_LABEL>}

\textcolor[RGB]{126,126,126}{\rule{\linewidth}{1pt}}

{\tiny
    {\color{red}
        <REVIEW_HEADER>
        <REPORT>
    }
}

\textcolor[RGB]{126,126,126}{\rule{\linewidth}{1pt}}

\typeout{END OF <REVIEW_LABEL>}

""".replace(
            "<REVIEW_LABEL>", label
        )
        # role, task, what was provided for review
        .replace("<REVIEW_HEADER>", review_header).replace("<REPORT>", report)
    )


def _review_section(
    client: GenAIClient, doc: LatexDocument, section_ref: ContentReferenceBase
):
    role = "Domain Expert"

    if isinstance(section_ref, PreSectionRef):
        content_to_review = "Pre-section"
        yield from []
        return

    elif isinstance(section_ref, SectionRef):
        if section_ref.in_appendix:
            content_to_review = (
                f"Section '{section_ref.title}' in the appendix "
                f"(label: '{section_ref.generated_label}')"
            )
        else:
            content_to_review = f"Section '{section_ref.title}'"

    else:
        raise ValueError(f"Invalid part type: {section_ref}")

    content_provided_for_review = "Entire paper"

    task = f"Proofread single part of paper ({content_to_review})"

    print(f" - Proofreading: {role}: {task}")

    review_reports: str = client.make_query(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            INSTRUCTIONS_PROMPT
            # -
            .replace("{LATEX_CONTENT}", to_latex(doc))
            # -
            .replace(
                "<FOCUS>",
                f"Your task is to review one part of the paper, namely {content_to_review}. "
                f"The entire paper is provided so you can understand the context. "
                f"However, your task is to only review the selected section. ",
            )
        ),
        label=f"{role}: {task}",
    )

    review_header = (
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

    yield section_ref, _wrap_report(
        report=review_reports,
        review_header=review_header,
        label=f"{role}: {task}",
    )


def _proofread_abstract_and_intro_vs_paper(
    client: GenAIClient, doc: LatexDocument
) -> Tuple[ContentReferenceBase, str]:
    role = "Domain Expert"
    task = "Check that the abstract and introduction match the rest of the paper"
    content_to_review = "Entire paper"

    print(f" - Proofreading: {role}: {task}")

    intro_and_abstract_report: str = client.make_query(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            INSTRUCTIONS_PROMPT
            # -
            .replace("{LATEX_CONTENT}", to_latex(doc))
            # -
            .replace(
                "<FOCUS>",
                "Your only task is to review the abstract and introduction: "
                "Check that these give a good summary of the rest of the paper. "
                "In your report, treat the abstract and introduction separately. ",
            )
        ),
        label=f"{role}: {task}",
    )

    review_header = (
        (
            r"\textbf{Role:} \emph{<ROLE>} \\"
            r"\textbf{Task:} \emph{<TASK>} \\"
            r"\textbf{Content provided for review:} \emph{<CONTENT_TO_REVIEW>}"
            r"\\ \\"
        )
        .replace("<ROLE>", role)
        .replace("<TASK>", task)
        .replace("<CONTENT_TO_REVIEW>", content_to_review)
    )

    # This report should be added before the first section
    first_ref = list(doc.content_dict.keys())[0]

    return first_ref, _wrap_report(
        report=intro_and_abstract_report,
        review_header=review_header,
        label=f"{role}: {task}",
    )


def invalid_latext_guard(client: GenAIClient):
    def f(x: Tuple[ContentReferenceBase, str]) -> Tuple[ContentReferenceBase, str]:
        """
        GenAI may return invalid latex. This function will catch that and attempt to
        fix LaTeX errors.
        """
        section_ref, report = x

        return x

    return f


def proofread_paper(
    doc: LatexDocument,
    report_output_filepath: Path,
) -> LatexDocument:
    """
    Connect to LLM API and proofread the section.
    """
    log_output_path: Path = report_output_filepath.parent / "logged-gen-ai-queries"

    client = GenAIClient(log_output_path=log_output_path, max_tokens=1000)

    guard = invalid_latext_guard(client)

    def _get_reports():
        # Emit proofreading reports. Reports are added to the document in order FIFO.
        yield guard(_proofread_abstract_and_intro_vs_paper(client, doc))

        for section_ref in doc.content_dict.keys():
            yield from map(guard, _review_section(client, doc, section_ref))

    for k, v in _get_reports():
        doc = add_comments(doc, k, [v])

    return doc
