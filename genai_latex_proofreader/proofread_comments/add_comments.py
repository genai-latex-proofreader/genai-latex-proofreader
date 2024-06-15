from dataclasses import replace

from ..latex_interface.data_model import ContentReferenceBase, LatexDocument


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
