from ...genai_interface.anthropic import GenAIClient
from ...latex_interface.data_model import (
    ContentReferenceBase,
    LatexDocument,
    PreSectionRef,
    SectionRef,
)
from ..formatting import format_report, make_review_comment_header

SYSTEM_PROMPT: str = """
You are an elite-level editor and proofreader with over 20 years of experience in
academic and scientific writing across diverse fields.

Your expertise is characterized by:

Linguistic precision:
- Exceptional ability to identify and correct grammatical errors, typos, and
  inconsistencies in language usage.
- Proficiency in multiple English dialects (US, UK, Australian, Canadian) and their
  specific conventions and nuances.
- Expertise in improving clarity, coherence, and flow of academic and scientific texts.

Style Guide Mastery:
- In-depth knowledge of major academic style guides like APA, MLA, Chicago and IEEE.

Broad Cross-Disciplinary Knowledge:
- Broad understanding of terminology and conventions across STEM fields,
  social sciences, humanities, and interdisciplinary studies.
- Capability to verify the appropriate use of specialized terms and concepts within
  their respective fields.
- Your expertise spans multiple academic disciplines, allowing you to understand and
  improve specialized terminology across various fields.

Technical Proficiency:
- Expert knowledge of LaTeX typesetting, including advanced features and custom macros.
- Preference for working directly with LaTeX source files to ensure optimal
  formatting and structure.

Ethical Editing:
- Commitment to maintaining the author's voice and intent while improving the overall
  quality of the text.
- Ability to provide constructive feedback that helps authors develop their writing
  skills.

Attention to Detail:
- Meticulous review process that catches even minor inconsistencies in formatting,
  referencing, and data presentation.
- Keen eye for improving visual elements such as tables, figures, and equations for
  clarity and impact.

Your editing approach is characterized by precision, thoroughness, and a commitment to
elevating the quality of academic and scientific communication. Authors value your
feedback for its depth, clarity, and actionable nature, consistently resulting in
polished, professional manuscripts ready for high-impact publication.
"""

INSTRUCTIONS_PROMPT: str = r"""
Your task is to proofread and suggest improvement on the provided {FOCUS} from an
academic paper under review. Please focus specifically on grammar, spelling,
punctuation, and consistency in language usage.

The material to proofread is provided in the latex_to_proofread-tag below:
<latex_to_proofread>
{LATEX_CONTENT}
</latex_to_proofread>

Please focus on the following aspects:
- Grammar: Identify and correct any grammatical errors.
- Spelling: Spot and correct any spelling mistakes or typos.
- Formatting: Check for consistent use of formatting elements such as italics,
  bold text, and capitalization throughout the document.
- Punctuation: Ensure proper use of punctuation throughout the text.
- Consistency: Check for consistent use of eg. British or American English throughout.
- Clarity: While maintaining the author's voice, suggest minor rewording where it
  might improve clarity. Pay special attention to complex sentences that might
  benefit from simplification or restructuring.
- Flow: Identify any areas where transitions between sentences or paragraphs could
  be improved for better readability.

Your task is only to focus on the language usage in the paper.
- Do not proofread or comment on the scientific content of the paper.
- Do not proofread or suggest improvements on the use of Latex.
These tasks are handled by other experts.

Format your proofreading report as follows:

For each issue you find, provide the correction and a brief explanation or motivation.

Write up all your findings as a LaTeX-enumerated list following the structure as in
the <example_proofread_report> tag below. Your review must begin with
"\begin{enumerate}" (without the quotes).

- Your proofreading report will be copy-pasted into the paper and then compiled.
- Therefore, your report must be valid LaTeX. Eg., when referencing a formula,
  always surround the formula with dollar signs, not quotation signs.
- You can reference existing labels in the paper.
- Start each entry with a short summary of what should be changed.
  "\item Section \section{sec:development}: typo: what to change"
- Make it easy to understand how to apply your suggestions. Eg. avoid suggestions like
    - Replace (long sentense) with (long sentence).
  These make it difficult to understand what to do. Rather indicate the modification, eg.,
    - In (long sentence) add a comma before "we say".
  You can also boldface the parts to focus on, include words to add in in brackets,
  or strikeout words that should be removed.

<example_proofread_report>
\begin{enumerate}
\item Section \ref{sec:foo}: typo: In the sentense "After this this setup," replace $\kappa_P$ with $\kappa_p$.
\item After equation \eqref{foo}: grammar: ...
\end{enumerate}
Conclude with a short summary of your findings.
</example_proofread_report>

Your report should be thorough but concise (aim for 15-20 key points). Focus on
the most significant issues that improve readability and professionalism.
"""


def proofread_one_section_for_language(
    client: GenAIClient,
    doc: LatexDocument,
    section_ref: ContentReferenceBase,
):
    role = "English language expert"

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

    task = f"""Proofread "{content_to_review}" of paper"""

    print(f" - {role}: {task}")

    section_content: str = "\n".join(doc.content_dict[section_ref])

    review_reports: str = client.make_query(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            INSTRUCTIONS_PROMPT
            # -
            .replace("{LATEX_CONTENT}", section_content)
            # -
            .replace("{FOCUS}", "section")
        ),
        label=f"{role}: {task}",
    )

    yield section_ref, format_report(
        report=review_reports,
        review_comment_header=make_review_comment_header(
            role=role, task=task, content_provided_for_review=content_to_review
        ),
        label=f"{role}: {task}",
    )


def proofread_abstract_for_language(
    client: GenAIClient,
    doc: LatexDocument,
) -> str:
    if not r"\begin{abstract}" in doc.begin_document:
        print("Skipped: No abstract found to proofread for language")
        return ""

    role = "English language expert"
    content_to_review = "The abstract"

    task = f"""Proofread "{content_to_review}" of paper"""

    print(f" - {role}: {task}")

    section_content: str = "\n".join(doc.begin_document)

    review_reports: str = client.make_query(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            INSTRUCTIONS_PROMPT
            # -
            .replace("{LATEX_CONTENT}", section_content)
            # -
            .replace("{FOCUS}", "abstract")
        ),
        label=f"{role}: {task}",
    )

    return format_report(
        report=review_reports,
        review_comment_header=make_review_comment_header(
            role=role, task=task, content_provided_for_review=content_to_review
        ),
        label=f"{role}: {task}",
    )
