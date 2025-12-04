# Project Specification: v-shell (GitVoice)

## Overview
v-shell (internally referred to as GitVoice) is a voice-controlled shell assistant designed to enable hands-free Git operations. It leverages Large Language Models (LLMs) and Speech-to-Text (STT) technologies to interpret natural language voice commands and execute corresponding Git actions.

## Goals
- Provide a seamless voice interface for common Git workflows.
- Ensure safety and reliability with confirmation steps for destructive actions.
- Support multiple LLM and STT providers for flexibility.
- Maintain a modular and extensible architecture.

## Core Features

### Voice Interaction
- **Wake Word Detection**: (Planned/In-progress) Activation via "hey git".
- **Speech-to-Text**: Transcription of voice commands using providers like Faster-Whisper or Groq.
- **Natural Language Understanding**: Interpretation of user intent using LLMs (Groq, Gemini, Ollama).

### Git Operations
Supported commands include:
- `git status`: Check repository status.
- `git log`: View commit history.
- `git diff`: Show changes.
- `git add .`: Stage all changes.
- `git commit`: Commit changes with AI-generated or user-provided messages.
- `git push`: Push commits to remote.
- `git pull`: Pull changes from remote.
- `git reset`: specific reset modes (soft, mixed, hard).
- `git checkout`: Switch branches.
- `git branch`: Create new branches.
- `smart commit`: Automatically stage, generate message (with user confirmation), commit, and push.
- `run tests`: Run project tests (e.g., pytest).

### Safety & Configuration
- **Tool Policies**: Granular control over safety and retries via `ToolPolicy`.
    - **Confirmation**: Required for destructive actions (push, pull, commit, reset).
    - **Retries**: Automatic retries for flaky commands (e.g., network issues, test failures).
- **Configurable Providers**: Switch between different LLM and STT backends via `config.py` / `.env`.
- **Metrics**: Usage logging to `metrics.jsonl` for debugging and analysis.

## Architecture

1.  **Audio Input**: Captures user voice.
2.  **STT Engine**: Transcribes audio to text (English enforced).
3.  **LLM Router**: Analyzes text to determine intent and extract parameters (Tool Calling).
4.  **Tool Policy**: Checks safety requirements and retry configuration.
5.  **Git Executor**: Safely executes the determined Git command using `GitPython`.
6.  **Feedback**: Returns success/failure status and output to the user (via CLI/TTS).

## Tech Stack
- **Language**: Python 3.x
- **Core Libraries**:
    - `pydantic`: Data validation and settings management.
    - `GitPython`: Interaction with Git repositories.
- **AI/ML**:
    - `faster-whisper` / `groq`: Speech-to-Text.
    - `groq` / `google-generativeai` / `ollama`: LLM inference.
- **Testing**: `pytest`

## Project Structure
- `app/`: Main application source code.
    - `core/`: Core logic (models, executor).
    - `audio/`: Audio recording and processing.
    - `llm/`: LLM integration and routing.
    - `cli/`: User interface.
- `tests/`: Test suite.
