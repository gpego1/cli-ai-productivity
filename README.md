# CLI AI — LLM-Powered Productivity CLI

A command-line productivity tool that leverages Large Language Models to help you extract insights from your files. Summarize documents, ask questions about their content, and generate detailed data analysis reports — all from your terminal.

## Features

### `summarize`
Extracts the key information from a file and returns a concise, structured summary with bullet points. Supports `.txt`, `.md`, `.pdf`, and `.csv` files.

### `ask`
Ask a natural-language question about the contents of a file. The LLM answers based **only** on the document's content, so you get grounded, accurate responses. Supports `.txt`, `.md`, `.pdf`, and `.csv` files.

### `report`
Generates an in-depth statistical analysis report from a `.csv` file. The tool uses **pandas** to compute descriptive statistics and value counts, then sends the data to the LLM for expert-level interpretation covering data quality, distributions, anomalies, and actionable recommendations. The report is saved as a timestamped `.txt` file in the `output/` directory.

## Supported File Types

| Extension | Used by              |
|-----------|----------------------|
| `.txt`    | summarize, ask       |
| `.md`     | summarize, ask       |
| `.pdf`    | summarize, ask       |
| `.csv`    | summarize, ask, report |

## Requirements

- Python 3.10+
- An OpenAI-compatible API endpoint (e.g. [LM Studio](https://lmstudio.ai/), [Ollama](https://ollama.com/) with OpenAI compatibility, or the OpenAI API itself)

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/gpego1/cli-ai.git
cd cli-ai
```

2. **Create and activate a virtual environment**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
BASE_URL=http://127.0.0.1:1234/v1
OPENAI_API_KEY=lm-studio
MODEL=gemma-3
```

| Variable        | Description                                                        |
|-----------------|--------------------------------------------------------------------|
| `BASE_URL`      | The base URL of your OpenAI-compatible API server                  |
| `OPENAI_API_KEY`| API key (use any non-empty string for local servers like LM Studio)|
| `MODEL`         | The model name to use for inference                                |

> **Tip:** If you're using LM Studio, start the local server, load a model, and use the values shown above. For OpenAI's API, set `BASE_URL=https://api.openai.com/v1` and provide your real API key.

## Usage

```bash
python main.py <command> [arguments]
```

### Summarize a file

```bash
python main.py summarize path/to/document.pdf
```

Returns a structured summary with the main points extracted from the document.

### Ask a question about a file

```bash
python main.py ask path/to/document.md "What are the key deadlines mentioned?"
```

The LLM reads the document and answers your question using only the information it contains.

### Generate a CSV report

```bash
python main.py report path/to/data.csv
```

Produces a detailed statistical analysis and saves it as a `.txt` file in the `output/` directory with a timestamp (e.g. `output/20260627_143022.txt`).

### Show help

```bash
python main.py --help
python main.py <command> --help
```

## Project Structure

```
cli-ai/
├── main.py              # Entry point — argument parser and command routing
├── commands/
│   ├── ask.py           # Ask command — Q&A over file content
│   ├── summarize.py     # Summarize command — document summarization
│   └── report.py        # Report command — CSV statistical analysis
├── utils/
│   ├── call_llm.py      # LLM client wrapper (OpenAI-compatible)
│   └── file_reader.py   # Multi-format file reader (.txt, .md, .pdf, .csv)
├── output/              # Generated report files (auto-created)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not tracked by git)
└── .gitignore
```

## How It Works

1. **File Reading** — The `file_reader` module detects the file extension and extracts its text content. PDFs are processed with `pdfplumber`, CSVs are parsed with Python's `csv` module (or `pandas` for reports), and text/markdown files are read directly.

2. **Prompt Engineering** — Each command constructs a task-specific prompt that includes the extracted content and clear instructions for the LLM.

3. **LLM Inference** — The prompt is sent to an OpenAI-compatible API endpoint via the `openai` Python SDK. The response is returned to the user or saved to a file.

## License

This project is open source. Feel free to use, modify, and distribute it.
