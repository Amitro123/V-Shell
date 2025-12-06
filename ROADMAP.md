# Development Roadmap

Based on the [Code Review](./CODE_REVIEW.md), the following roadmap outlines the path to a robust and feature-complete v-shell.

## Phase 1: Stabilization & Completeness (Immediate)

The goal of this phase is to ensure that all features advertised to the AI are actually executable and that the application is responsive.

1.  **Implement Missing Git Tools**
    - **Task**: Create implementations for the following tools in `app/core/tools/git_ops/` and register them in `execute_tool`:
        - `git.log` (View history)
        - `git.add_all` (Explicit stage)
        - `git.reset` (Undo changes)
        - `git.checkout_branch` & `git.create_branch` (Branch management)
    - **Goal**: Resolve the "Unknown tool" errors for valid commands.

2.  **Non-Blocking Git Operations**
    - **Task**: Refactor `app/core/executor.py` and `git_ops` to run `GitPython` commands in a thread pool (using `asyncio.to_thread`).
    - **Goal**: Prevent UI freezes during large pushes, pulls, or diffs.

3.  **Refactor Safety Logic**
    - **Task**: Remove the hardcoded safety heuristics in `app/llm/router.py` and ensure `app/core/policies.py` is the single source of truth for confirmation requirements.
    - **Goal**: Simplify maintenance and ensure consistent safety rules.

## Phase 2: Enhanced Capabilities (Short Term)

4.  **Refined Smart Commit**
    - **Task**: Improve `smart_commit_push` to handle untracked files more intelligently (e.g., ask "Do you want to add untracked file X?").
    - **Task**: Move commit message generation logic out of the `Brain` class.

5.  **Docker Integration**
    - **Task**: Implement the placeholder `docker` tools (`docker.ps`, `docker.logs`, `docker.compose_up`).
    - **Goal**: Expand the assistant's scope beyond just Git.

## Phase 3: Advanced Intelligence (Medium Term)

6.  **Context-Aware Intent**
    - **Task**: Inject the current `git status` summary into the LLM's system prompt dynamically.
    - **Goal**: Enable commands like "fix the error in that file" or "why is this file modified?".

7.  **Interactive Conflict Resolution**
    - **Task**: Detect merge conflicts during `pull` and offer a voice-guided wizard to resolve them (e.g., "Keep ours" or "Keep theirs").

8.  **Wake Word Integration**
    - **Task**: Re-evaluate `openwakeword` integration once dependency issues are resolved to enable true hands-free activation.
