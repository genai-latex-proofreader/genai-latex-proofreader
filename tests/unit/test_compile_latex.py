from pathlib import Path

from genai_latex_proofreader.compile_latex import compile_latex


def test_compile_latex():
    # test that we can compile dummy LaTeX document
    files = {
        Path(
            "main.tex"
        ): rb"""
            \documentclass{article}
            \begin{document}
            Hello, world!
            \end{document}
        """
    }
    result = compile_latex(files, Path("main.tex"))[-1]

    assert result.returncode == 0
    assert result.output_files[Path("main.pdf")].startswith(b"%PDF-1.5")


def test_compile_latex_with_bibliography():
    # test that we can compile dummy LaTeX document with a bibliography
    files = {
        Path(
            "main.tex"
        ): rb"""
            \documentclass{article}
            \begin{document}
            Hello, world!
            \cite{test}
            \bibliographystyle{plain}
            \bibliography{references}
            \end{document}
        """,
        Path("references.bib"): b"@article{test, title={Test}, author={Test Author}}",
    }
    result = compile_latex(files, Path("main.tex"))[-1]

    assert result.returncode == 0
    assert result.output_files[Path("main.pdf")].startswith(b"%PDF-1.5")
