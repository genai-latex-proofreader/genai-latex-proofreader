# GenAI LaTeX Proofreader

**GenAI LaTeX Proofreader** is an automated tool that uses generative AI to proofread and suggest improvements to scientific papers written in LaTeX.
The suggestions are appended into the orignal LaTeX source file creating a proofreading report.
This tool is primarily intended for authors working on a scientific paper.

In more detail, the generated proofreading report contains the original paper under review, with a list of suggestions attached to the beginning of each section.
For each section, feedback is created from the perspective of different proofreading personas.
For example, when writing a paper, these could be "Domain expert", "English language expert" and "Book editor".
However, the personas could also include additional personas such as "Statistical reviewer", "LaTeX specialist" or "Inclusive language expert" depending on the topic of the paper.

Here "proofreading" should be interpreted broadly.
While current large language models (LLMs) have an understanding of logic, mathematics and physics, LLMs should not be trusted for any serious proofreading of scientific results.
Thus, any suggestions should be evaluated critically.

GenAI LaTeX Proofreader require a subscription to the [Anthropic API](https://www.anthropic.com).

### Example proofreading reports
- TBD
- TBD

## Features
Completely automated proofreading of LaTeX documents.
- To create a proofreading report, one only needs to run a Python script. It will make calls to a GenAI API and automatically generate a proofreading report (in pdf format).
- E.g., if the paper is under version control in GitHub, one can use GitHub runners to automatically generate a proofreading report whenever a new version of the paper is checked in.

### Supported proofreading personas

#### ✅ Domain expert (implemented)
- Critically evaluate each section for correctness, clarity. Identify strengths, weaknesses and provide suggestions for future work.
- Also evaluate how well the title, abstract and introduction match the content of the rest of the paper.
- Implementation with prompts [here](genai_latex_proofreader/genai_proofreader/proofreaders/domain_expert.py).

#### ✅ Language expert (implemented)
- Proofread the content for typos, wording, grammar and flow.
- Implementation with prompts [here](genai_latex_proofreader/genai_proofreader/proofreaders/language_expert.py).

#### 🚧 Book editor (not yet implemented)
- Evaluate the high-level organization of the paper.

#### 🚧 LaTeX specialist (not yet implemented)
- Give feedback on your use of LaTeX.

#### 🚧 Custom proofreading personas
In addition to the above, one can add other proofreading personas. However, this currently requires that one edit the Python source code.

The idea of using different AI personas for proofreading is introduced in Ethan Mollick's book [Co-Intelligence: Living and working with AI](https://www.amazon.com/Co-Intelligence-Living-Working-Ethan-Mollick/dp/059371671X) published 4/2024.

## Limitations
- Some structure is assumed for the paper. E.g.
   - Content before the first `\section{..}` will not be proofread.
   - Unnumbered sections are not supported `\section*{..}`.
   - The content of any included files will not be visible to the proofreader.
- The GenAI will not see or understand any images.
- The GenAI will not have access to any references.
- The proofreading report will not be deterministic. Different runs with the same input document may generate different reports.
- There are multiple providers that offer access to LLMs, like OpenAI, Anthropic, Google. Currently only Anthropic is supported.
- Your paper will be sent over the internet to the LLM provider. Please carefully read their terms of service.
- Using LLMs will also incur some cost.
- Uses pdflatex and TexLive. TexLive is also used by arxiv, [link](https://info.arxiv.org/help/faq/texlive.html).
- The proofreading comments returned by the LLM provided will in some cases include LaTeX errors. GenAI LaTeX Proofreader will attempt to fix these. However, in some cases the proofreading report may fail to compile.


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

For a medium size paper, this will take a few minutes.
If everything worked, the proofreading report can be found in `output/report.pdf`.

### Configuration and customization

Depending on the topic of your paper, you may want to adjust the prompts that define the proofreading personas. Currently the prompts need to be edited directly in the Python source code.

# Generative AI

**GenAI LaTeX Proofreader** uses GenAI (Generative AI) and large language models (LLM) to automate proofreading of scientific papers.
As of 2024, GenAI is a quickly evolving technology with rapid developments.

The below list contain some references and related works that may be helpful to learn more about this topic, and more broadly about using AI to advance scientific discovery:

- 12/2023, Microsoft Research, *The Impact of Large Language Models on Scientific Discovery: a Preliminary Study using GPT-4*
    - https://arxiv.org/pdf/2311.07361

- 10/2023, W. Liang et al., *Can large language models provide useful feedback on research papers? A large-scale empirical analysis*
    - https://arxiv.org/abs/2310.01783
    - https://github.com/Weixin-Liang/LLM-scientific-feedback

- 6/2023, *AI to Assist Mathematical Reasoning: A Workshop* organized by National Academies of Sciences.
   - https://www.nationalacademies.org/event/06-12-2023/ai-to-assist-mathematical-reasoning-a-workshop
   - Collection of resources collected as part of the workshop: https://docs.google.com/document/d/1kD7H4E28656ua8jOGZ934nbH2HcBLyxcRgFDduH5iQ0/edit


# Contributions

Contributions or ideas are welcome!

# License

"GenAI LaTeX Proofreader" is copyright 2024 Matias Dahl (and contributors), and distributed under the terms of the MIT open source license.

Portions of this work has been developed using AI-powered tools.

For details, please see the [LICENSE](LICENSE.md) file.