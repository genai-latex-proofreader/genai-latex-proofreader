from dataclasses import dataclass, replace
from typing import Callable, Iterable, Optional, Tuple

from genai_latex_proofreader.utils.splitters import (
    split_at_first_lambda,
    split_list_at_lambda,
    split_list_at_lambdas,
)

from .data_model import ContentReferenceBase, LatexDocument, PreSectionRef, SectionRef


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
    *detect_prefix: str,
) -> Callable[[str], _DetectedLineMatch | None]:
    def f(line):
        if any(line.startswith(prefix) for prefix in detect_prefix):
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


# --- Functions to parse Sections ---


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


def _extract_sections(
    lines: list[str], is_appendix: bool
) -> dict[ContentReferenceBase, list[str]]:
    """
    Internal function to extract sections from a list of lines.
    """
    pre_sections, sections = split_list_at_lambda(
        lines, _create_line_prefix_detector(r"\section")
    )
    return {
        PreSectionRef(in_appendix=is_appendix): pre_sections,
        **{
            SectionRef(
                in_appendix=is_appendix,
                title=_parse_arg_to_latex_command(
                    r"\section", new_section_line.matched_line
                ),
                label=_extract_label(section_lines),
                generated_label=_generated_label(
                    section_idx=section_idx, is_appendix=is_appendix
                ),
            ): section_lines
            for section_idx, (new_section_line, section_lines) in enumerate(sections)
        },
    }


def _parse_content_to_sections(
    lines: list[str],
) -> Tuple[
    dict[ContentReferenceBase, list[str]],
    Optional[dict[ContentReferenceBase, list[str]]],
]:
    pre_appendix_lines, appendix_line, post_appendix_lines = split_at_first_lambda(
        lines, _create_line_match_detector(r"\appendix")
    )
    # is there an \appendix in the document (potentially empty)?
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


# --- Bibliography parsing ---

# Patterns to detect start of (optional) bibliography
# (A line starting with any of these is considered the first line of the bibliography)
BIBLIOGRAPHY_STARTS = [
    r"\bibliography",
    r"%\bibliography",
    r"\begin{thebibliography}",
    "% --- bibliography ---",
]


_bibliography_start_detector = _create_line_prefix_detector(*BIBLIOGRAPHY_STARTS)


def _is_comment_line(line: str) -> bool:
    return (
        line.startswith("%")
        # -
        and _bibliography_start_detector(line) is None
    )


def parse_from_latex(input_latex: str) -> LatexDocument:
    """
    Main interface to parse an input LaTeX document into LatexDocument data model
    """
    latex_document: list[str] = [
        line.strip() for line in input_latex.split("\n") if not _is_comment_line(line)
    ]
    print(f" - Read {len(latex_document)} lines (after removing comment lines)")

    no_content, splits = split_list_at_lambdas(
        latex_document,
        [
            _create_line_prefix_detector(r"\documentclass"),
            _create_line_match_detector(r"\begin{document}"),
            _create_line_match_detector(r"\maketitle"),
            _bibliography_start_detector,
            _create_line_match_detector(r"\end{document}"),
        ],
    )
    if len(no_content) > 0:
        raise Exception(
            rf"parse_latex: \documentclass expected to be at start of of file."
        )

    if len(splits) not in [4, 5]:
        raise Exception(
            f"parse_latex: expected 4 (no bibliography) or 5 (with bibliography) "
            f"splits, but got {len(splits)}."
        )

    # create empty LatexDocument
    result = LatexDocument(
        pre_matter=[],
        begin_document=[],
        content_dict={},
        bibliography=[],
    )

    # fill with parsed components
    for line, content in splits:
        if line.matched_line.startswith(r"\documentclass"):
            result = replace(result, pre_matter=[line.matched_line, *content])
        elif line.matched_line == r"\begin{document}":
            result = replace(result, begin_document=content)
        elif line.matched_line == r"\maketitle":
            main_content_dict, optional_appendix_content_dict = (
                _parse_content_to_sections(content)
            )
            if optional_appendix_content_dict is None:
                result = replace(result, content_dict=main_content_dict)
            else:
                result = replace(
                    result,
                    content_dict={
                        **main_content_dict,
                        **optional_appendix_content_dict,
                    },
                )

        elif _bibliography_start_detector(line.matched_line) is not None:
            result = replace(result, bibliography=[line.matched_line, *content])
        elif line.matched_line == r"\end{document}":
            if len(content) > 0:
                raise Exception(
                    r"Did not expect content after \end{document}. Please delete."
                )
        else:
            raise Exception(f"Unexpected line: {line}")

    # Raise exception if there are duplicate labels in the sections (incl. Appendix
    # sections). Also check that source Latex document does not use the same labels as
    # (our internal) labels generated when parsing the Latex.
    def _get_labels() -> Iterable[str]:
        for ref in result.content_dict.keys():
            if isinstance(ref, SectionRef):
                if ref.label is not None:
                    yield ref.label
                yield ref.generated_label

    if len(list(_get_labels())) != len(set(list(_get_labels()))):
        raise Exception(
            "Duplicate labels detected among sections. Please fix. "
            f"Current labels: {_get_labels()}."
        )

    return result
