from dataclasses import replace

from ..genai_interface.anthropic import GenAIClient
from ..latex_interface.data_model import LatexDocument
from ..proofread_comments.add_comments import add_comments
from .latex_guard import LatexGuard
from .proofreaders.domain_expert import (
    proofread_abstract_and_intro_vs_paper_content,
    proofread_one_section,
)


def proofread_paper(client: GenAIClient, doc: LatexDocument) -> LatexDocument:
    """
    Top level function to proofread a paper using GenAI and attach reports them to the
    input Latex document.
    """
    # ensure that the color package is included in report
    doc = replace(doc, pre_matter=doc.pre_matter + [r"\usepackage{color}"])

    latex_guard = LatexGuard(client, doc)

    def _get_reports():
        # Emit all proofreading reports
        yield latex_guard(proofread_abstract_and_intro_vs_paper_content(client, doc))

        for section_ref in doc.content_dict.keys():
            yield from map(latex_guard, proofread_one_section(client, doc, section_ref))

    for k, v in _get_reports():
        doc = add_comments(doc, k, [v])

    return doc
