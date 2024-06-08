from dataclasses import replace

from ..latex_interface.data_model import LatexDocument, LatexSection, LatexSections
from .data_model import SectionComment, SectionRef


def _add_comment(
    latex_section: LatexSection,
    section_comment: SectionComment,
) -> LatexSection:
    # if comments define new sections, the original section numbers will be messed up
    if any(
        forbidden_command in section_comment.comments
        for forbidden_command in [r"\section", r"\subsection", r"\subsubsection"]
    ):
        raise ValueError(
            f"Section comment should not define any section:s, subsection:s, or subsubsection:s."
        )

    return replace(
        latex_section,
        content=section_comment.comments + latex_section.content,
    )


def _add_comment_to_sections(
    sections: LatexSections,
    section_ref: SectionRef,
    section_comment: SectionComment,
) -> LatexSections:
    # check that the requested replacemnt section label exists

    all_labels = [section.label for section in sections.sections]
    if section_ref.section_label not in all_labels:
        raise ValueError(
            f"Section {section_ref.section_label} not found among {all_labels}."
        )

    return replace(
        sections,
        sections=[
            (
                _add_comment(section, section_comment)
                if section_ref.section_label in section.labels()
                else section
            )
            for section in sections.sections
        ],
    )


def add_comments(
    doc: LatexDocument, comments: dict[SectionRef, SectionComment]
) -> LatexDocument:
    """
    Add proofreading comments to a LaTeX document.
    """
    for section_ref, section_comment in comments.items():
        if section_ref.in_appendix:
            assert doc.appendix is not None
            doc = replace(
                doc,
                appendix=_add_comment_to_sections(
                    doc.appendix, section_ref, section_comment
                ),
            )
        else:
            doc = replace(
                doc,
                main_document=_add_comment_to_sections(
                    doc.main_document, section_ref, section_comment
                ),
            )
    return doc
