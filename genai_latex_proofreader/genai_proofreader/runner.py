from dataclasses import replace

from ..genai_interface.anthropic import GenAIClient
from ..latex_interface.data_model import LatexDocument, PreSectionRef
from ..proofread_comments.add_comments import add_comments
from .formatting import project_plug
from .latex_guard import LatexGuard
from .proofreaders.domain_expert import (
    proofread_one_section_by_expert,
    proofread_title_abstract_and_intro_vs_paper_by_domain_expert,
)
from .proofreaders.language_expert import (
    proofread_abstract_for_language,
    proofread_one_section_for_language,
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

        # Language expert: proofread abstract
        yield latex_guard(
            (
                PreSectionRef(in_appendix=False),
                proofread_abstract_for_language(client, doc),
            )
        )

        # Domain expert: check abstract vs paper content
        yield latex_guard(
            proofread_title_abstract_and_intro_vs_paper_by_domain_expert(client, doc)
        )

        # LaTeX guard should not be necessary since plug is a constant.
        yield latex_guard(
            (
                PreSectionRef(in_appendix=False),
                project_plug(),
            )
        )

        # Language + Domain experts: review each section
        for section_ref in doc.content_dict.keys():
            yield from map(
                latex_guard,
                proofread_one_section_for_language(client, doc, section_ref),
            )
            yield from map(
                latex_guard,
                proofread_one_section_by_expert(client, doc, section_ref),
            )

    for k, v in _get_reports():
        doc = add_comments(doc, k, [v])

    return doc
