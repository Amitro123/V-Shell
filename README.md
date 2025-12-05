# 🎙️ v-shell (GitVoice)

> **Hands-free Git operations powered by AI.**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)

**v-shell** (internally GitVoice) is your intelligent voice-controlled assistant for Git. Stop typing repetitive commands and start talking to your repository. Powered by state-of-the-art LLMs and Speech-to-Text technology, it understands your intent and executes Git operations safely and efficiently.

---

## ✨ Key Features

- 🗣️ **Voice-Activated**: Just say "Hey Git" (coming soon) or trigger the listener to start.
- 🧠 **Natural Language Understanding**: Don't memorize flags. Just say "undo the last commit" or "push to main".
- 🛡️ **Safety First**: Critical commands (like `push`, `reset`, `commit`) require your confirmation.
- 🔄 **Robustness**: Automatic retries for flaky commands and network issues.
- 📊 **Metrics**: Tracks usage stats for improvement.
- 🔌 **Model Agnostic**: Bring your own keys! Supports **Groq**, **Gemini**, **Ollama**, and **Faster-Whisper**.
- ⚡ **Fast & Efficient**: Optimized for low-latency interactions.

## 🏗️ Architecture

```mermaid
flowchart TD
    User([User]) -->|Voice Command| Audio[Audio Input]
    Audio -->|WAV| STT[STT Engine\n(Faster-Whisper)]
    STT -->|Text| Router[LLM Router\n(Brain)]
    Router -->|ToolCall| Policy{Tool Policy\n(Safety Gate)}
    
    Policy -->|Safe/Confirmed| Executor[Git Executor]
    Policy -->|Unsafe/No Confirm| Cancel([Cancel])
    
    Executor -->|Execute| Git[(Git Repository)]
    Git -->|Result| Executor
    Executor -->|Feedback| User
    
    subgraph Core Logic
    Router
    Policy
    Executor
    end
```

## 🛠️ Tech Stack

- **Core**: Python 3.x, Pydantic, GitPython
- **AI/ML**: Faster-Whisper, Groq API, Google Gemini, Ollama
- **CLI**: Rich terminal interface (planned)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A microphone
- API Keys for Groq or Gemini (optional but recommended for best performance)

### Installation

```bash
# Clone the repository
git clone https://github.com/Amitro123/V-Shell.git
cd V-Shell

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -e .
```

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your API keys:
   ```ini
   GROQ_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   ```

## 🎤 Usage

Start the assistant:

```bash
python -m app.main
```

**Try saying:**
- *"Check the status"*
- *"Stage all changes"*
- *"Smart commit"* (Stages, generates message, confirms, commits, and pushes)
- *"Run tests"*
- *"Pull from origin"*
- *"Push to origin main"*

## 📂 Project Structure

```
v-shell/
├── app/
│   ├── audio/      # 🎧 Audio recording & STT
│   ├── core/       # ⚙️ Core logic & execution
│   ├── llm/        # 🧠 LLM routing & intelligence
│   └── cli/        # 🖥️ User Interface
├── tests/          # 🧪 Test suite
└── ...
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
