from dataclasses import dataclass
from typing import Optional

# --- Data model for parsed LaTeX document ---

# --- Data models to reference content in LaTeX document ---


@dataclass(frozen=True)
class ContentReferenceBase:
    """
    Data model to reference a content part in a LaTeX document
    """

    # Is the content is in main part of document (in_appendix=False)
    # or in appendix (in_appendix=True)
    in_appendix: bool


class PreSectionRef(ContentReferenceBase):
    r"""
    Reference content before a \section{...}.

    Field `in_appendix` determines if content is in the main document or in
    the appendix.
    """

    pass


@dataclass(frozen=True)
class SectionRef(ContentReferenceBase):
    r"""
    Reference content (in main doc, or appendix) before the first \section{...}

    Field `in_appendix` determines if content is in the main document or in
    the appendix.
    """

    # Title of the section, eg. "Introduction", determined by "\section{Introduction}".
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
        # TODO: delete this and all dependencies
        # assert False
        return ([self.label] if self.label is not None else []) + [self.generated_label]


@dataclass(frozen=True)
class LatexSections:
    pre_sections: list[str]
    sections: list[LatexSection]
    content_dict: dict[ContentReferenceBase, list[str]]


@dataclass(frozen=True)
class LatexDocument:
    # --- start of document ---
    pre_matter: list[str]

    # --- \begin{document} ---

    begin_document: list[str]

    # Note:
    #   \begin{abstract} ... \end{abstract} is in "begin_document"

    # --- \maketitle ---

    # all sections, including sections in appendix
    # dict key order determine section order (with optional Appendix sections last)
    content_dict: dict[ContentReferenceBase, list[str]]

    bibliography: list[str]

    # --- \end{document} ---

    def filter_content_dict(
        self, is_appendix: bool
    ) -> dict[ContentReferenceBase, list[str]]:
        return {
            section_ref: content
            for section_ref, content in self.content_dict.items()
            if section_ref.in_appendix == is_appendix
        }


def to_latex(obj: LatexDocument) -> str:
    """
    Convert a parsed LaTeX document back into a LaTeX document string.
    """

    def _emit_content_dict(content_dict: dict[ContentReferenceBase, list[str]]):

        # input does not cross border between appendix and main document
        assert len(set(k.in_appendix for k in content_dict.keys())) == 1

        for section_ref, content in content_dict.items():
            if isinstance(section_ref, PreSectionRef):
                yield from content

            elif isinstance(section_ref, SectionRef):
                yield rf"\section{{{section_ref.title}}}"
                # A latex section can have multiple labels. If no label is
                # assigned in the source document, we here ensure that this
                # section has a label (eg. that can be used to reference the
                # section from review comments).
                yield rf"\label{{{section_ref.generated_label}}}"
                yield from content

    def _to_latex(obj: LatexDocument):

        yield from obj.pre_matter
        yield r"\begin{document}"
        yield from obj.begin_document
        yield r"\maketitle"

        yield from _emit_content_dict(obj.filter_content_dict(is_appendix=False))

        # optional appendix
        appendix_content_dict = obj.filter_content_dict(is_appendix=True)
        if len(appendix_content_dict) > 0:
            yield r"\appendix"
            yield from _emit_content_dict(appendix_content_dict)

        # bibliography end matters
        yield from obj.bibliography
        yield r"\end{document}"

    return "\n".join(_to_latex(obj))


def to_summary(obj: LatexDocument) -> str:
    """
    Return a summary of the parsed LaTeX document.
    """

    def _emit_content_dict_summary(content_dict: dict[ContentReferenceBase, list[str]]):

        # input does not cross border between appendix and main document
        assert len(set(k.in_appendix for k in content_dict.keys())) == 1

        for section_ref, content in content_dict.items():
            if isinstance(section_ref, PreSectionRef):
                yield f" - Pre-section ({len(content)} lines)"

            elif isinstance(section_ref, SectionRef):
                yield f" - Section '{section_ref.title}', label: '{section_ref.label}', {len(content)} lines"
                yield f"    - generated_label: {section_ref.generated_label}"

    def _summary(obj):
        yield f"Pre-matter: {len(obj.pre_matter)} lines"
        yield f"Begin document: {len(obj.begin_document)} lines"

        yield from _emit_content_dict_summary(
            obj.filter_content_dict(is_appendix=False)
        )

        appendix_content_dict = obj.filter_content_dict(is_appendix=True)
        if len(appendix_content_dict) > 0:
            yield r"--- Appendix ---"
            yield from _emit_content_dict_summary(appendix_content_dict)

        yield f"Bibliography: {len(obj.bibliography)} lines"

    return "\n".join(_summary(obj))
