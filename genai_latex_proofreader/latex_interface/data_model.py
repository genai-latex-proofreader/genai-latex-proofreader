from dataclasses import dataclass
from typing import Optional

# --- Data model for parsed LaTeX document ---


@dataclass(frozen=True)
class LatexSection:
    # Title of the section, eg., determined by "\section{Introduction}".
    title: str

    # Optional label for this section given in input Latex document,
    # eg., with a \label{sec:intro} command.
    #
    # If the input document contains more than one \label{...} for this section,
    # this will only contain the first label, eg., "sec:intro".
    #
    # If Section contains no \label{...} in the input document, this is None.
    label: Optional[str]

    # All sections will be given a generated label when the input Latex document
    # is parsed. This will ensure we can refer to sections also when no label is given
    # in the input Latex document.
    generated_label: str

    # Section content (including subsections, \label{..}, but not \section{})
    content: list[str]

    def labels(self) -> list[str]:
        """
        Return Latex labels for this section.
        """
        return ([self.label] if self.label is not None else []) + [self.generated_label]


@dataclass(frozen=True)
class LatexSections:
    pre_sections: list[str]
    sections: list[LatexSection]


@dataclass(frozen=True)
class LatexDocument:
    # --- start of document ---
    pre_matter: list[str]

    # --- \begin{document} ---

    begin_document: list[str]

    # Note:
    #   \begin{abstract} ... \end{abstract} is in "begin_document"

    # --- \maketitle ---

    main_document: LatexSections

    # --- \appendix ---

    appendix: Optional[LatexSections]

    bibliography: list[str]

    # --- \end{document} ---


def to_latex(obj: LatexDocument | LatexSection | LatexSections) -> str:
    """
    Convert a parsed LaTeX document back into a LaTeX document string.
    """

    def _to_latex(obj):
        match obj:
            case LatexSection(title, label, generated_label, content):
                yield rf"\section{{{title}}}"
                # A latex section can have multiple labels. If no label is assigned
                # in the source document, we here ensure that this section has a label.
                yield rf"\label{{{generated_label}}}"
                yield from content

            case LatexSections(pre_sections, sections):
                yield from pre_sections
                for section in sections:
                    yield from _to_latex(section)

            case _ if isinstance(obj, LatexDocument):
                yield from obj.pre_matter
                yield r"\begin{document}"
                yield from obj.begin_document
                yield r"\maketitle"

                yield from _to_latex(obj.main_document)

                if obj.appendix is not None:
                    yield r"\appendix"
                    yield from _to_latex(obj.appendix)

                yield from obj.bibliography
                yield r"\end{document}"

            case _:
                raise Exception(f"Unknown input to to_latex: {obj}")

    return "\n".join(_to_latex(obj))
