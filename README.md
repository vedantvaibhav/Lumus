# Self-Quiz Generator Agent

A powerful AI-powered tool that generates quizzes from any document, webpage, or text source.

## Features

### 🌐 Web Interface
- **Interactive UI**: Beautiful, responsive web interface
- **Real-time generation**: Watch quizzes being created in real-time
- **Visual analytics**: Charts and metrics for quiz analysis
- **One-click downloads**: Export in multiple formats instantly
- **Sample content**: Built-in examples to get started quickly

### 🧠 Core Capabilities
- **Multi-source support**: PDFs, web pages, text files
- **Intelligent quiz generation**: Multiple choice and short answer questions
- **Difficulty rating**: Easy, medium, hard questions
- **Multiple export formats**: JSON, CSV, HTML, Anki
- **Clean text extraction**: Removes headers, HTML tags, and formatting

## Quick Start

### 🌐 Web UI (Recommended for Testing)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Launch the web interface:
```bash
python launch_ui.py
```

3. Open your browser to `http://localhost:8501`

4. Enter your Google API key and start generating quizzes!

### 💻 Command Line Interface

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google API key:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

3. Generate a quiz from a webpage:
```bash
python main.py --source "https://en.wikipedia.org/wiki/Photosynthesis" --output quiz.json
```

4. Generate a quiz from a PDF:
```bash
python main.py --source "document.pdf" --output quiz.json
```

## Usage Examples

```python
from quiz_generator import QuizGenerator

# Initialize the generator
generator = QuizGenerator()

# Generate quiz from URL
quiz = generator.generate_from_url("https://example.com/article")

# Generate quiz from PDF
quiz = generator.generate_from_pdf("document.pdf")

# Generate quiz from text
quiz = generator.generate_from_text("Your text content here...")
```

## Project Structure

```
├── src/
│   ├── agents/
│   │   ├── reader_agent.py      # Text extraction from various sources
│   │   └── quiz_maker_agent.py  # AI-powered quiz generation
│   ├── core/
│   │   ├── orchestrator.py      # Coordinates agents
│   │   └── models.py           # Data models and schemas
│   ├── utils/
│   │   ├── formatters.py       # Export formats (JSON, CSV, HTML)
│   │   └── text_cleaner.py     # Text preprocessing utilities
│   └── cli.py                  # Command-line interface
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```
