from dataclasses import dataclass
from ftplib import all_errors
from typing import Callable, Iterable, Optional, Tuple

from genai_latex_proofreader.utils.splitters import (
    split_at_first_lambda,
    split_list_at_lambda,
    split_list_at_lambdas,
)

from .data_model import LatexDocument, LatexSection, LatexSections


def _parse_arg_to_latex_command(latex_command: str, line: str) -> str:
    r"""
    Parse argument to a latex-commands.

    Examples:
    parse_latex_parameter(r"\subsection", r"\subsection{foo}") = "foo"

    Input line is assumed to be trimmed so that when there is a
    match, there are no spaces before/after eg "\subsection{foo}".

    Raises ValueError if line does not start with latex_command.
    """
    if line.startswith(latex_command):
        result = line.replace(latex_command, "", 1)
        assert result[0] == "{"
        assert result[-1] == "}"
        return result[1:-1]

    raise ValueError(f"Expected '{line}' to start with '{latex_command}'.")


@dataclass(frozen=True)
class _DetectedLineMatch:
    matched_line: str


def _create_line_prefix_detector(
    detect_prefix: str,
) -> Callable[[str], _DetectedLineMatch | None]:
    def f(line):
        if line.startswith(detect_prefix):
            return _DetectedLineMatch(line)
        return None

    return f


def _create_line_match_detector(
    detect_prefix: str,
) -> Callable[[str], _DetectedLineMatch | None]:
    def f(line):
        if line == detect_prefix:
            return _DetectedLineMatch(line)
        return None

    return f


def _extract_label(lines: list[str]) -> Optional[str]:
    r"""
    Find first label (eg \label{mylabel}) before any subsections, or subsubsections.
    If no label is found, return None
    """
    for line in lines:
        if line.startswith(r"\label"):
            return _parse_arg_to_latex_command(r"\label", line)
        elif line.startswith(r"\subsection") or line.startswith(r"\subsubsection"):
            break

    return None


def _generated_label(section_idx: int, is_appendix: bool) -> str:
    if is_appendix:
        return f"sec:genai:generated:label:appendix:{section_idx}"

    return f"sec:genai:generated:label:{section_idx}"


def _extract_sections(lines: list[str], is_appendix: bool) -> LatexSections:
    """
    Internal function to extract sections from a list of lines.
    """
    pre_sections, sections = split_list_at_lambda(
        lines, _create_line_prefix_detector(r"\section")
    )
    return LatexSections(
        pre_sections=pre_sections,
        sections=[
            LatexSection(
                title=_parse_arg_to_latex_command(
                    r"\section", new_section_line.matched_line
                ),
                label=_extract_label(section_lines),
                generated_label=_generated_label(
                    section_idx=section_idx, is_appendix=is_appendix
                ),
                content=section_lines,
            )
            for section_idx, (new_section_line, section_lines) in enumerate(sections)
        ],
    )


def _parse_content_to_sections(
    lines: list[str],
) -> Tuple[LatexSections, Optional[LatexSections]]:
    pre_appendix_lines, appendix_line, post_appendix_lines = split_at_first_lambda(
        lines, _create_line_match_detector(r"\appendix")
    )
    # is there an appendix?
    if appendix_line is None:
        # no
        assert len(post_appendix_lines) == 0
        assert lines == pre_appendix_lines
        return _extract_sections(lines, is_appendix=False), None
    else:
        return (
            _extract_sections(pre_appendix_lines, is_appendix=False),
            _extract_sections(post_appendix_lines, is_appendix=True),
        )


def parse_from_latex(input_latex: str) -> LatexDocument:
    """
    Main interface to parse an input LaTeX document into LatexDocument data model
    """
    latex_document: list[str] = [line.strip() for line in input_latex.split("\n")]
    print(f" - Read {len(latex_document)} lines")

    no_content, splits = split_list_at_lambdas(
        latex_document,
        [
            _create_line_prefix_detector(r"\documentclass"),
            _create_line_match_detector(r"\begin{document}"),
            _create_line_match_detector(r"\maketitle"),
            _create_line_prefix_detector(r"\bibliography"),
            _create_line_match_detector(r"\end{document}"),
        ],
    )
    if len(no_content) > 0:
        raise Exception(
            rf"parse_latex: \documentclass expected to be at start of of file."
        )

    if len(splits) != 5:
        raise Exception(f"parse_latex: expected 5 splits, got {len(splits)}")

    # Parse main parts of the document
    (
        (slash_documentclass_line, post_documentclass_lines),
        (_begin_document, post_begin_document_lines),
        (_maketitle, post_maketitle_lines),  # = main body of document
        (slash_bibliography_line, post_bibliography_lines),
        (_end_document, _post_end_document_lines),
    ) = splits

    # delete variables with no information
    del _begin_document, _maketitle, _end_document

    if len(_post_end_document_lines) > 0:
        raise Exception(r"Did not expect content after \end{document}. Please delete.")
    del _post_end_document_lines

    # Parse sections and any sections in the appendix
    main_document, optional_appendix = _parse_content_to_sections(post_maketitle_lines)

    result = LatexDocument(
        pre_matter=[slash_documentclass_line.matched_line, *post_documentclass_lines],
        begin_document=post_begin_document_lines,
        main_document=main_document,
        appendix=optional_appendix,
        bibliography=[slash_bibliography_line.matched_line, *post_bibliography_lines],
    )

    # Raise exception if there are duplicate labels among sections (incl. Appendix
    # sections). Also check that input document does not use same
    # labels as generated ones.
    def _get_labels() -> Iterable[str]:
        for section in main_document.sections:
            yield from section.labels()

        if optional_appendix is not None:
            for section in optional_appendix.sections:
                yield from section.labels()

    if len(list(_get_labels())) != len(set(list(_get_labels()))):
        raise Exception(
            "Duplicate labels detected among sections. Please fix. "
            f"Current labels: {_get_labels()}."
        )

    return result
