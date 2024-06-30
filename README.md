# GenAI LaTeX Proofreader

**GenAI LaTeX Proofreader** is an automated tool that uses generative AI to proofread and suggest improvements to scientific papers written in LaTeX.
It is primarily intended for authors working on a scientific paper.
The generated proofreading report contains the original paper under review, with a list of suggestions attached to the beginning of each section.
For each section, feedback is created from the perspective of different proofreading personas.
For example, when writing a paper, these could be "Domain Expert", "Language Expert" and "Book editor".
However, the personas could also include additional personas such as "Statistical Reviewer", "Latex Specialist" or "Accessibility Expert" depending on what is needed.

Here "proofreading" should be interpreted broadly.
While current large language models (LLMs) have an understanding of logic, mathematics and physics, LLMs should not be trusted for any serious proofreading of scientific results.
Thus, any suggestions should be evaluated critically.

To run `genai-latex-proofreader` you will need access to the Anthropic API.

### Example proofreading reports
- TBD
- TBD

## Features
Completely automated proofreading of LaTeX documents.
- To create a proofreading report, one only needs to run a Python script. It will make calls to a GenAI API and automatically generate a proofreading report (in pdf format).
- E.g., if the paper is under version control in GitHub, one can use GitHub runners to automatically generate a proofreading report whenever a new version of the paper is checked in.

### Supported proofreading personas

#### Domain expert (implemented)
- Critically evaluate the content for correctness, clarity. Identify strengths, weaknesses and provide suggestions for future work.
- Evaluate how well the abstract and introduction match the content of the rest of the paper.
- The prompt defining this expert can be found [here](genai_latex_proofreader/genai_proofreader/proofreaders/domain_expert.py).

#### Language expert (not yet implemented)
- Proofread the content for typos, wording, grammar and flow.

#### Book editor (not yet implemented)
- Evaluate the high-level organization of the paper.

#### LaTeX specialist (not yet implemented)
- Give feedback on your use of LaTeX.

One can add additional proofreading personas (by editing the code).

## Limitations
- Some structure is assumed for the paper. E.g.
   - Content before the first `\section{..}` will not be proofread.
   - Unnumbered sections are not supported `\section*{..}`.
   - The content of any included files will not be visible to the proofreader.
- The GenAI will not see or understand any images.
- The GenAI will not have access to any references.
- There are multiple providers that offer access to LLMs, like OpenAI, Anthropic, Google. Currently only Anthropic is supported.
- Your paper will be sent over the internet to the LLM provider. Please carefully read their terms of service.
- Using LLMs will also incur some cost.
- Uses pdflatex and TexLive. TexLive is also used by arxiv, [link](https://info.arxiv.org/help/faq/texlive.html).

# Getting started

Note that this work is an early proof of concept. Thus some familiarity with the development tools (git, Python, Docker, Anthropic API access) may be needed to get this working.

The below steps (for Mac/Linux-based systems) describe how to proofread a paper:

Step 1: Clone the [repo](https://github.com/genai-latex-proofreader/genai-latex-proofreader)
```bash
git clone git@github.com:genai-latex-proofreader/genai-latex-proofreader.git
cd genai-latex-proofreader
```

Step 2: Build the Docker container (with Python and Latex)
```bash
(cd .devcontainer/latex; make build)
```

Step 3: Set up secret token to the Anthropic API, see https://docs.anthropic.com/en/docs/quickstart

```bash
export ANTHROPIC_API_KEY='your-secret-api-key-here'
```

(Note: do not share your `ANTHROPIC_API_KEY`)

Step 4: Copy files required to build your paper from your directory into the repo directory into the `paper-to-proofread` subdirectory.
```bash
mkdir paper-to-proofread
cp -R /path/to/your/paper/ paper-to-proofread
```

For testing you can use a dummy paper `tests/integration/assets/empty_paper.tex` provided in the repo.

```bash
mkdir paper-to-proofread
cp -R tests/integration/assets/ paper-to-proofread/
```

(Note: Please always have a backup of your paper.)

Step 5: Run `genai-latex-proofreader`

```bash
(cd .devcontainer/latex; docker compose run --rm --entrypoint "python3" genai-latex-proofreader-service -m genai_latex_proofreader.cli --input_latex_path paper-to-proofread/empty_paper.tex --output_report_filepath output/report.tex)
```

If everything worked, the proofreading report can be found in `output/report.pdf`.

Depending on the topic of your paper, you may want to adjust the prompts that define the proofreading personas. See above.

# Contributions

Contributions or ideas are welcome!

# License

"GenAI LaTeX Proofreader" is copyright 2024 Matias Dahl (and contributors), and distributed under the terms of the MIT license.

Portions of this work has been developed with the assistance of AI-powered tools.

For details, please see the [LICENSE](LICENSE.md) file.