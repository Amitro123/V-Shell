# v-shell

Voice-controlled shell assistant

## Project Structure

```
v-shell/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── config.py            # Application configuration
│   ├── audio/               # Audio processing
│   │   ├── __init__.py
│   │   ├── recorder.py      # Audio recording functionality
│   │   └── stt.py           # Speech-to-text
│   ├── llm/                 # LLM integration
│   │   ├── __init__.py
│   │   ├── router.py        # LLM routing logic
│   │   └── commit_message.py # Commit message generation
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py        # Data models
│   │   └── executor.py      # Command execution
│   └── cli/                 # CLI interface
│       ├── __init__.py
│       └── ui.py            # User interface
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_executor.py
│   └── test_router.py
├── .env.example             # Environment variables template
├── .gitignore
├── pyproject.toml           # Project configuration
└── README.md
```

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Configuration

1. Copy `.env.example` to `.env`
2. Fill in your API keys and configuration values

## Usage

```bash
# Run the application
python -m app.main
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy app/
```

## License

TBD
