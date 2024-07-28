"""
Latex expert that can fix Latex errors returned by the GenAI API.

Latex errors are corrected using GenAI calls.
"""

import uuid
from pathlib import Path
from typing import Tuple

from genai_latex_proofreader.compile_latex import CommandResult, compile_latex_doc
from genai_latex_proofreader.genai_interface.anthropic import GenAIClient
from genai_latex_proofreader.latex_interface.data_model import (
    ContentReferenceBase,
    LatexDocument,
)
from genai_latex_proofreader.proofread_comments.add_comments import add_comments
from genai_latex_proofreader.utils.splitters import split_list_at_lambda

from ..genai_interface.anthropic import GenAIClient


def _make_fix_latex_errors_query(
    label: str, client: GenAIClient, latex_snippet: str, error_messages: str
) -> str:

    SYSTEM_PROMPT: str = r"""You are an expert in LaTeX typesetting."""

    INSTRUCTIONS: str = (
        r"""
The snippet provided below between <provided-snipped>-tags is from a larger LaTeX file,
and it does not compile.

Some LaTeX errors might have been provided between <errors>-tags below.

Please correct any errors in the snippet so that it compiles as LaTeX without errors.
The output should be valid LaTeX.

- Return the snippet with the LaTeX errors corrected.
- The snipped will be copy pasted into a larger LaTeX document so do not add any preamble or document environment.
- Modify the input as little as possible.
- Do not preface your answer with "Here is the corrected snippet:" or similar comments. Only return the corrected LaTeX.
- Do not make any other changes or additions to the snippet.
- Do not explain what changes you made.
- If there are unmatched curly braces, add/close curly braces as needed based on the context.
- If there are unmatched environments (eg., \begin{itemize}), then open/close environments as needed based on the context.
- If commands miss arguments, then fill in suitable dummy values. Eg. correct $1 \frac$ with $1 \frac{?}{?}$.
- If there are undefined LaTeX commands, enclose then in \texttt or \mathtt and replace \ with \textbackslash or \backslash.
- Do not add any new text (not before or after the snippet). Only fix the LaTeX error(s) in the existing text.
- Do not enclose your response in <snippet>-tags.
- If the input is valid LaTeX, return the input as-is without any changes.

<provided-snipped>
<LATEX_SNIPPET_WITH_ERRORS>
</provided-snipped>

<errors>
<ERRORS_LOGGED_FROM_SNIPPED>
</errors>
""".replace(
            "<LATEX_SNIPPET_WITH_ERRORS>", latex_snippet
        ).replace(
            "<ERRORS_LOGGED_FROM_SNIPPED>", error_messages
        )
    )

    return client.make_query(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=INSTRUCTIONS,
        label=label,
    )


def _doc_compiles(doc: LatexDocument) -> CommandResult:
    return compile_latex_doc(doc, Path("main.tex"))[-1]


def _latex_guard(
    client: GenAIClient,
    doc: LatexDocument,
    content_ref: ContentReferenceBase,
    content: str,
) -> str:
    # unmodified document should not have errors
    if (input_run := _doc_compiles(doc)).returncode != 0:
        raise Exception(
            f"latex guard: input does not compile \n"
            f"returncode  :  {input_run.returncode} \n"
            f"stdout      :  {input_run.stdout} \n"
            f"stderr      :  {input_run.stderr} \n"
        )
    del input_run

    # add new content into input document;
    #  - Surround modified content with "\typeout{<RUN_ID>}" Latex commands.
    #  - This allows us to separate the Latex errors from the modification
    #    in output logs
    run_id = f"run-id={uuid.uuid4()}"
    run_id_line = r"\typeout{<RUN_ID>}".replace("<RUN_ID>", run_id)

    new_lines = [run_id_line, content, run_id_line]
    modified_latex = add_comments(doc, content_ref, new_lines)

    if (out := _doc_compiles(modified_latex)).returncode == 0:
        return content

    else:
        stdout: list[str] = out.stdout.split("\n")

        _, [[_, log_lines_from_modification], *_] = split_list_at_lambda(
            stdout, lambda x: x if run_id in x else None
        )

        corrected_content = _make_fix_latex_errors_query(
            label="latex-guard",
            client=client,
            latex_snippet=content,
            error_messages="\n".join(log_lines_from_modification),
        )
        return corrected_content


class LatexGuard:
    """
    GenAI may return invalid LaTeX. This class provide way to catch that and attempt to
    fix any LaTeX errors in generated proofreading reports (using the GenAI API client).
    """

    def __init__(self, client: GenAIClient, doc: LatexDocument, retries: int = 3):
        self.client = client
        self.doc = doc
        self.retries = retries

    def __call__(
        self, x: Tuple[ContentReferenceBase, str]
    ) -> Tuple[ContentReferenceBase, str]:
        print("LaTeX guard: Checking that generated content is valid LaTeX")
        part_ref, content = x
        for retry in range(self.retries):
            if retry > 0:
                print(f"LaTeX guard retry {retry + 1} of {self.retries}")

            content = _latex_guard(self.client, self.doc, part_ref, content)
            if (
                _doc_compiles(
                    add_comments(self.doc, part_ref, [content]),
                ).returncode
                == 0
            ):
                if retry == 0:
                    print("LaTeX guard: generated content compiles as is")
                else:
                    print("LaTeX guard: generated content fixed")
                return part_ref, content

        print("LaTeX guard: Unable to fix problems in generated content")
        return (
            part_ref,
            r"\textbf{Unable LaTeX errors in the below:}\n \n \n" + content,
        )
