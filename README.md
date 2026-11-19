# AI Research Agent

An AI-powered research app that takes a topic, searches the web, reads a source, and produces a structured report with a critic review. It includes a Streamlit interface and a command-line pipeline.

## How it works

The workflow combines two tool-using agents with two LLM chains:

1. **Search agent** uses Tavily to find recent web results and source URLs.
2. **Reader agent** scrapes the first result URL for page text.
3. **Writer chain** drafts a report with an introduction, key findings, conclusion, and sources.
4. **Critic chain** reviews and scores the report, listing strengths and areas to improve.

The Streamlit app presents the report, critic feedback, source links, and raw data, and lets you download the report as Markdown.

## Requirements

- Python 3.10 or later
- A [Groq API key](https://console.groq.com/keys)
- A [Tavily API key](https://app.tavily.com/)

## Setup

From the project directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install streamlit langchain langchain-core langchain-groq python-dotenv requests beautifulsoup4 tavily-python rich
```

Copy the example environment file and replace the placeholders with your API keys:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set `GROQ_API_KEY` and `TAVILY_API_KEY`. Keep `.env` private; it is excluded by `.gitignore`.

## Run the app

Start the Streamlit interface:

```powershell
streamlit run app.py
```

Open the local URL printed in the terminal, enter a research topic, and select **Run research**.

Alternatively, run the command-line pipeline:

```powershell
python pipeline.py
```

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit UI for submitting topics and viewing or downloading results |
| `Agents.py` | Search and scraper agents, plus writer and critic chains |
| `pipeline.py` | Orchestrates the search, scraping, report-writing, and review steps |
| `tools.py` | Tavily web search and webpage scraping tools |

## Screenshots

### Command-line pipeline

![Command-line research pipeline and critic output](<Screenshot 2026-11-19 162014.png>)

### Project workspace

![Project files in VS Code](<Screenshot 2026-11-19 163233.png>)

### Streamlit report output

![Completed research report in the Streamlit app](<Screenshot 2026-11-19 164045.png>)

![Another generated research report](<Screenshot 2026-11-19 165428.png>)

### Critic review tab

![Critic review tab in the Streamlit app](<Screenshot 2026-11-19 170308.png>)

## Note

Web results and generated reports can be incomplete or inaccurate. Verify important claims against the linked sources.
