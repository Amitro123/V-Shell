from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ToolPolicy:
    confirmation_required: bool
    retries: int
    retry_on_exit_codes: List[int] = field(default_factory=list)

TOOL_POLICIES: Dict[str, ToolPolicy] = {
    "git_status": ToolPolicy(False, 0, []),
    "run_tests": ToolPolicy(False, 1, [1]),
    "git_diff": ToolPolicy(False, 0, []),
    "git_pull": ToolPolicy(True, 0, []),
    "smart_commit_push": ToolPolicy(True, 1, [1]),
    "git_push": ToolPolicy(True, 1, [1]),
    "git_commit": ToolPolicy(True, 0, []),
    "git_reset": ToolPolicy(True, 0, []),
    "git_checkout_branch": ToolPolicy(True, 0, []),
}
