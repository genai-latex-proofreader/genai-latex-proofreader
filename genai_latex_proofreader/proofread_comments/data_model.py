from dataclasses import dataclass

# --- Data model to contain proofreading comments ---


@dataclass(frozen=True)
class SectionRef:
    """
    Data model to reference a section in a LaTeX document
    """

    in_appendix: bool
    section_label: str


class ProofreadingComment:
    pass


@dataclass(frozen=True)
class SectionComment(ProofreadingComment):
    """
    Data model for comments about one section (or section in appendix).

    In the proofreading report, this would be added to the begininning of the section.
    """

    comments: list[str]
