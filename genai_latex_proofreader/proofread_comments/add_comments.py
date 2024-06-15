from dataclasses import replace

from ..latex_interface.data_model import (
    ContentReferenceBase,
    LatexDocument,
    LatexSection,
    LatexSections,
)
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
    doc: LatexDocument,
    section_ref: ContentReferenceBase,
    comments: list[str],
) -> LatexDocument:
    """
    Add proofreading comments to a LaTeX document.
    """
    if any(
        forbidden_command in comments
        for forbidden_command in [r"\section", r"\subsection", r"\subsubsection"]
    ):
        raise ValueError(
            f"Section comment should not define any section:s, subsection:s, or subsubsection:s."
        )

    if not section_ref in doc.content_dict:
        raise ValueError(f"Section reference {section_ref} not found in document.")

    return replace(
        doc,
        content_dict={
            _section_ref: (comments if _section_ref == section_ref else []) + content
            for _section_ref, content in doc.content_dict.items()
        },
    )
