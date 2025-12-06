# Code Review: v-shell (GitVoice)

**Date:** 2024-05-22
**Reviewer:** Jules (AI Agent)

## 1. Overview
This review analyzes the current state of the `v-shell` project against its specifications (`spec.md`), documentation (`README.md`, `AGENTS.md`), and best practices. The project aims to be a voice-controlled Git assistant using hybrid AI (local SetFit + LLM).

## 2. Findings

### 2.1. Tool Discrepancies (Critical)
There is a significant mismatch between the tools advertised to the LLM (`app/llm/router.py`) and the tools actually implemented and registered (`app/core/executor.py`).

-   **Missing Tools**: The Router advertises `git.commit` (with message) and `git.push` (with remote/branch), but these are **not registered** in `executor.py`.
    -   *Impact*: If the LLM router chooses `git.commit` or `git.push` (instead of `smart_commit_push`), the execution will fail with "Unknown tool".
-   **Parameter Mismatch**:
    -   `git.reset`: Router prompt advertises `commits` parameter, but implementation (`git_ops/reset.py`) expects `steps`.
    -   `git.branch`: Router correctly uses `create` boolean, and `executor.py` maps it to `git_checkout_branch`, which is good.
-   **Aliases**: `git.add_all` is correctly mapped. `git.status` is correct.

### 2.2. Safety & Confirmation Logic
The safety mechanism is split and potentially inconsistent.
-   **Router vs. Policy**: `app/llm/router.py` sets `confirmation_required=True` dynamically for dangerous actions. However, `app/main.py` relies primarily on `TOOL_POLICIES` defined in `app/core/policies.py`.
    -   *Risk*: If `router.py` flags a command as unsafe but `TOOL_POLICIES` defaults to safe (or is missing the tool), the confirmation prompt might be skipped.
    -   *Current State*: `main.py` ignores `tool_call.confirmation_required`.
-   **Smart Commit**: `git.smart_commit_push` has embedded confirmation logic (callback) AND policy-based confirmation. This redundancy is confusing but currently safe.

### 2.3. Architecture & Code Quality
-   **Dependency injection**: `executor.py` injects `brain` into `smart_commit_push`. This is a bit leaky (tool knowing about the brain) but acceptable for this stage.
-   **Git Implementation**: The project uses `subprocess` calls to `git` CLI (via `git_ops/utils.py`) instead of `GitPython` for operations, despite `GitPython` being a dependency. This is actually good for performance and reducing blocking calls, but `GitPython` is still used in tests.
-   **Hardcoded Configuration**: `executor.py` has `SIMPLE_GIT_TOOLS` hardcoded. It should ideally be part of the registry or configuration.

### 2.4. Testing
-   **Coverage**: Core git operations (`git_ops`) and integration tests pass.
-   **Missing Dependencies**: Tests for `router` and `mcp` fail because `groq` and `fastmcp` libraries are missing in the test environment (or requirements).
-   **Mocking**: Tests rely heavily on mocking `subprocess`, which is fine, but integration tests with real git repos (like `test_integration_git.py`) are more valuable.

## 3. Recommendations & Action Plan

### 3.1. Immediate Fixes (Implemented in this PR)
1.  **Implement `git.commit` and `git.push`**: Add these atomic tools to `git_ops` and register them in `executor.py`.
2.  **Align `git.reset`**: Update Router prompt to use `steps` or map `commits` to `steps` in executor.
3.  **Unify Safety Checks**: Update `main.py` to respect **either** `policy.confirmation_required` OR `tool_call.confirmation_required`.

### 3.2. Future Improvements
1.  **Context Injection**: The `Brain` currently doesn't see the current git status or history when making decisions. Injecting `git status` output into the LLM system prompt would significantly improve "context-aware" commands.
2.  **Interactive Conflict Resolution**: As noted in roadmap, handling merge conflicts via voice is a killer feature.
3.  **Refined Router**: The SetFit classifier is a great optimization. Ensure it's retrained as new tools are added.
4.  **Feedback Loop**: Implement TTS (Text-to-Speech) to read back the commit message or status.

## 4. Suggestions for Development
-   **Keep `subprocess`**: Using `git` CLI via subprocess is robust. Stick to it.
-   **Enhance `smart_commit`**: Allow it to take a "hint" for the message from the user's voice command (e.g., "Smart commit with message 'fix login'").
-   **Pre-commit Hooks**: Add `pre-commit` to run tests and linters automatically.

