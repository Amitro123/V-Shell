# Agents

## User
The human developer interacting with the system via voice commands.
- **Role**: Initiates commands, provides confirmations, and reviews actions.
- **Capabilities**: Speaking commands, reading CLI output, approving destructive actions.

## GitVoice Assistant
The primary AI agent responsible for interpreting and executing commands.
- **Role**: Listens for commands, understands intent, executes Git operations, and provides feedback.
- **Components**:
    - **Listener**: Monitors audio input (Manual "Press Enter" Trigger).
    - **Transcriber**: Converts speech to text (Faster-Whisper).
    - **Interpreter**: Hybrid system:
        - **Fast Path**: SetFit model for local, instant intent classification.
        - **Slow Path**: LLM (Groq/Gemini) for complex reasoning.
    - **Tool Dispatcher (`execute_tool`)**: Routes `ToolCall` to modular implementations in `app/core/tools/`.
        - **Git Tools**: `git.status`, `git.log`, `git.add_all`, `git.reset`, `git.diff`, `git.branch`, `git.pull`, `git.smart_commit_push`, `git.run_tests`, `git.fetch`, `git.remote_list`, `git.stash_push`, `git.stash_pop`, `git.revert`, `git.merge`
        - **Docker Tools**: (Placeholder) `docker.*`
        - **System Tools**: (Placeholder) `system.*`
    - **MCP Server**: Exposes internal tools to external agents and IDEs.
    - **Reporter**: Reports results back to the User via CLI.

## System
The underlying operating system and Git environment.
- **Role**: Hosts the application and the Git repository.
- **Capabilities**: File system operations, network access (for push/pull), process execution.
