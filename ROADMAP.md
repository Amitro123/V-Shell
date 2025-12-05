# Development Roadmap

Based on the Code Review, here is a suggested path forward for v-shell development.

## Phase 1: Critical Fixes (Immediate)

1.  **Safety First: Smart Commit Confirmation**
    - **Task**: Modify `GitExecutor` and `main.py` to split `smart_commit_push` into two steps:
        1.  Stage & Generate Message.
        2.  **User Confirmation** (Display message).
        3.  Commit & Push.
    - **Goal**: Prevent bad commit messages from being pushed.

2.  **Dependency Management**
    - **Task**: Update `requirements.txt` to include `setfit` and `datasets`.
    - **Goal**: Ensure `pip install -r requirements.txt` results in a working application.

3.  **Missing Tests**
    - **Task**: Implement `tests/test_router.py`.
    - **Goal**: Verify that the "Brain" correctly routes text to tools, especially the safety overrides and fallback logic.

## Phase 2: UX Improvements (Short Term)

4.  **Better Audio Recording**
    - **Task**: Replace fixed-duration recording with:
        - "Press Enter to start, Press Enter to stop".
        - Or Voice Activity Detection (silence detection).
    - **Goal**: Eliminate the awkward 10-second wait or cut-off commands.

5.  **Feedback Loop**
    - **Task**: Add TTS (Text-to-Speech) output for success/failure messages (optional dependency).
    - **Goal**: True "hands-free" operation.

## Phase 3: Advanced Features (Medium Term)

6.  **Wake Word Integration**
    - **Task**: Integrate `openwakeword` to listen for "Hey Git" in a background thread.
    - **Goal**: seamless activation.

7.  **Interactive Conflict Resolution**
    - **Task**: Add a flow to handle merge conflicts (list conflicting files, offer "theirs/ours" choices via voice).
    - **Goal**: Handle complex git scenarios.

8.  **Context Awareness**
    - **Task**: Feed `git log` or `git status` output into the LLM context *before* asking for intent.
    - **Goal**: Allow commands like "undo that last change" (referring to the actual last commit).
