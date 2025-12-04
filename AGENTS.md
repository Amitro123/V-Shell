# Agents

## User
The human developer interacting with the system via voice commands.
- **Role**: Initiates commands, provides confirmations, and reviews actions.
- **Capabilities**: Speaking commands, reading CLI output, approving destructive actions.

## GitVoice Assistant
The primary AI agent responsible for interpreting and executing commands.
- **Role**: Listens for commands, understands intent, executes Git operations, and provides feedback.
- **Components**:
    - **Listener**: Monitors audio input for wake word or command trigger.
    - **Transcriber**: Converts speech to text.
    - **Interpreter**: Uses LLM to parse text into structured `ToolCall`s.
    - **Executor**: Performs the actual Git commands via `GitExecutor`.
    - **Reporter**: Reports results back to the User.

## System
The underlying operating system and Git environment.
- **Role**: Hosts the application and the Git repository.
- **Capabilities**: File system operations, network access (for push/pull), process execution.
