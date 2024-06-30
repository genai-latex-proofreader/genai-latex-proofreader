from typing import Tuple

from ...genai_interface.anthropic import GenAIClient
from ...latex_interface.data_model import (
    ContentReferenceBase,
    LatexDocument,
    PreSectionRef,
    SectionRef,
    to_latex,
)
from ..formatting import format_report, make_review_comment_header

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
- Use nested enumerate and itemize environments as appropriate.
- Your proofreading report will be copy-pasted into the paper and then compiled.
  Therefore your report must be valid Latex. Eg. do not write "please use the
  \align environment" since this is not valid Latex.
- You can reference existing labels in the paper.
- Your report should be concise and to the point, focusing on the most important issues.
  Keep your entire report below one page.

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


def proofread_one_section_by_expert(
    client: GenAIClient,
    doc: LatexDocument,
    section_ref: ContentReferenceBase,
):
    role = "Domain Expert"

    if isinstance(section_ref, PreSectionRef):
        # content before the first \section{} is not proofread
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

    task = f"Proofread '{content_to_review}' of paper"

    print(f" - {role}: {task}")

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

    yield section_ref, format_report(
        report=review_reports,
        review_comment_header=make_review_comment_header(
            role, task, content_provided_for_review
        ),
        label=f"{role}: {task}",
    )


def proofread_title_abstract_and_intro_vs_paper_by_domain_expert(
    client: GenAIClient, doc: LatexDocument
) -> Tuple[ContentReferenceBase, str]:
    role = "Domain Expert"
    task = "Check that the title, abstract and introduction match the rest of the paper"
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
                "Your only task is to review the title, abstract and introduction: "
                "Check that these give a good summary of the rest of the paper. "
                "In your report, treat the title, the abstract and introduction "
                "separately. ",
            )
        ),
        label=f"{role}: {task}",
    )

    # This report should be added before the first section
    first_ref = list(doc.content_dict.keys())[0]

    return first_ref, format_report(
        report=intro_and_abstract_report,
        review_comment_header=make_review_comment_header(role, task, content_to_review),
        label=f"{role}: {task}",
    )
