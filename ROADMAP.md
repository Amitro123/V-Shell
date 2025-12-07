# v-shell (GitVoice) – Roadmap

This roadmap tracks the evolution of v-shell from a voice-controlled Git assistant into a full Voice DevOps OS for developers.

---

## Phase 1 – Git Assistant Core (MVP)

**Goal:** Stable voice-first Git assistant with full Git workflow coverage and MCP integration.

### 1.1 Core Voice Flow

- [x] Manual recording control (press Enter to start/stop).
- [x] STT with Faster-Whisper / Groq.
- [x] Intent routing:
  - [x] Local SetFit classifier for common commands.
  - [x] LLM router (Groq) as fallback.
  - [x] Deterministic guards for compound commands  
        (e.g. “status, add, commit, push” → `git.smart_commit_push`).

### 1.2 Git Tools (v1)

- [x] `git.status` – concise repo status.
- [x] `git.diff` – diff (HEAD, optional path, origin/main).
- [x] `git.log` – recent history (`--oneline --decorate`).
- [x] `git.run_tests` – run test command (e.g. `pytest`) with summary.
- [x] `git.smart_commit_push`
  - [x] Show status.
  - [x] Stage changes (auto-stage).
  - [x] Generate commit message with LLM (single call + timeout/fallback).
  - [x] Commit and push to current branch.
- [x] `git.branch`
  - [x] Create new branch (`git checkout -b <name>`).
  - [x] Switch to existing branch (`git checkout <name>`).
  - [x] Basic name inference from phrases like “back to main branch”.
- [x] `git.reset` (safe)
  - [x] Limited to modes `hard/soft/mixed` and `HEAD~1..3`.
  - [x] Validations to prevent dangerous resets.

### 1.3 Safety, Policies & Metrics

- [x] `ToolCall` model with namespaced tool ids (`git.*`, future `docker.*`, `system.*`).
- [x] `TOOL_REGISTRY` – central mapping `tool_name -> async function`.
- [x] `ToolPolicy` for:
  - [x] `confirmation_required` (commit/push/reset/branch).
  - [x] retries / retryable exit codes.
- [x] Single confirmation flow in policy layer (keyboard `y/n` for now).
- [x] Metrics logging (e.g. `metrics.jsonl`):
  - [x] heard text
  - [x] tool name
  - [x] success / failure
  - [x] optional error / exit code.

### 1.4 MCP Server

- [x] MCP server module (`app/mcp/server.py`) using FastMCP / Python MCP SDK.
- [x] Exposed tools:
  - [x] `git.smart_commit_push`
  - [x] `git.branch`
  - [x] `git.reset`
- [x] Shared core executor between CLI and MCP:
  - [x] both call `execute_tool(ToolCall)`.

### 1.5 UI/UX & Feedback

**Goal:** Provide immediate sensory feedback so the user isn't guessing system state.

- [x] **Rich TUI integration**:
  - [x] Clear recording indicator (e.g. "🎙️ Listening…").
  - [x] Processing spinner for STT / LLM / tool execution.
  - [x] Pretty printing for `git status`, `git log`, `git diff`  
        (tables/panels with colors instead of raw text).
- [x] **Audio feedback placeholders**:
  - [x] Placeholder functions for "start listening" sound.
  - [x] Placeholder functions for "finished processing" sound.
  - [ ] Actual audio implementation (TODO: simpleaudio/playsound).
- [x] **Confirmation UX**:
  - [x] Keep keyboard `y/n` as baseline.
  - [ ] Optional voice confirmation mode (say "yes / no / cancel") when mic is active.

### 1.6 Testing & Docs

- [x] Unit tests for Git tools & executor.
- [x] Router tests (SetFit + LLM guards).
- [x] Integration tests with temporary Git repos.
- [x] High-level architecture diagram.
- [ ] Polished README with:
  - [ ] GIF / short video demo.
  - [ ] Example voice flows and MCP configuration.

---

## Phase 2 – Voice UX & Control

**Goal:** Make interaction feel more “assistant-like” and less keyboard-driven.

### 2.1 Silence-Based Segmentation (Optional Mode)

- [ ] `listen_until_silence()` helper:
  - [ ] Uses `speech_recognition` / PyAudio with `dynamic_energy_threshold`  
        to detect end of utterance.
  - [ ] Returns audio chunk for STT.
- [ ] CLI modes:
  - [x] `press-enter` (current stable mode).
  - [ ] `auto-silence` – Enter once → listen → each utterance triggers a flow.

### 2.2 Wake Word (Experimental)

- [ ] Integrate `openWakeWord` or similar library for a hotword like “V” / “Voice Agent”.
- [ ] Background wakeword listener process.
- [ ] On wakeword:
  - [ ] Call `listen_until_silence()` → STT → intent → tools.
- [ ] Configuration flag to enable/disable wakeword mode.

### 2.3 Stop / Cancel

- [ ] High-priority `system.stop` intent:
  - [ ] Phrases like “stop / cancel / abort” cancel the current operation ASAP.
  - [ ] At minimum, prevent further steps in multi-step flows (`smart_commit_push` etc.).

---

## Phase 3 – Context & Docker

**Goal:** Turn v-shell into a Voice DevOps assistant beyond Git, with smarter context.

### 3.1 Docker Tools

- [ ] `docker.build`
  - [ ] Build image (`docker build ...`), support `no_cache`, `tag`.
- [ ] `docker.compose_up` / `docker.compose_down`
  - [ ] Bring services up/down (e.g. `docker compose up -d`).
- [ ] `docker.ps` / `docker.logs`
  - [ ] List containers and tail logs for a service.

### 3.2 Project Context

- [ ] Project scanner on startup:
  - [ ] Detect stack from files like `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, etc.
  - [ ] Set default commands for:
    - [ ] `git.run_tests` (pytest / npm test / go test).
    - [ ] future `project.run` tool.

### 3.3 Smart Container Resolver

- [ ] Map fuzzy names (e.g. “the redis container”, “the database”)  
      to actual Docker container names/IDs using fuzzy matching over `docker ps`.

### 3.4 “Killer Demo”

- [ ] Record split-screen demo:
  - [ ] “V, rebuild the Docker image and clear the cache.”
  - [ ] “Now commit with message ‘refactor Docker config’ and push.”
- [ ] Use demo for README and LinkedIn content.

---

## Phase 4 – Advanced Intelligence

**Goal:** From “voice over tools” to a truly context-aware assistant.

- [ ] Context-aware intent:
  - [ ] Inject `git status` / `git log` summaries into LLM context  
        to handle commands like “undo that”, “fix that error”.
- [ ] Merge conflict assistant:
  - [ ] Detect conflicts after pull/merge.
  - [ ] Offer guided resolution options (“keep ours / keep theirs / show diff”).
- [ ] Wakeword hardening:
  - [ ] Collect real audio examples.
  - [ ] Tune wakeword thresholds / models for low false-positives.

---

## Phase 5 – Distribution & Install

**Goal:** Make it easy for others to install, configure, and run v-shell.

- [ ] `v-shell init` wizard:
  - [ ] Interactive setup for:
    - [ ] Groq (or other LLM) API keys.
    - [ ] Whisper/STT model selection.
    - [ ] Default test command / stack detection.
    - [ ] MCP enable/disable.
- [ ] Packaging:
  - [ ] Publish to PyPI (`pip install v-shell`).
  - [ ] Optional standalone binaries for Mac/Windows (no Python required).
- [ ] Basic upgrade path:
  - [ ] `v-shell upgrade` or clear instructions for updating versions.

---

*This file is living documentation. As features are implemented, update the checkboxes and link to issues/PRs for traceability.*