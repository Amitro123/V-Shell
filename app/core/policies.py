from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ToolPolicy:
    confirmation_required: bool
    retries: int
    retry_on_exit_codes: List[int] = field(default_factory=list)

TOOL_POLICIES: Dict[str, ToolPolicy] = {
    "git.status": ToolPolicy(False, 0, []),
    "git.log": ToolPolicy(False, 0, []),
    "git.add_all": ToolPolicy(False, 0, []),
    "git.run_tests": ToolPolicy(False, 1, [1]),
    "git.diff": ToolPolicy(False, 0, []),
    "git.pull": ToolPolicy(True, 0, []),
    "git.smart_commit_push": ToolPolicy(True, 1, [1]),
    "git.push": ToolPolicy(True, 1, [1]),
    "git.commit": ToolPolicy(True, 0, []),
    "git.reset": ToolPolicy(True, 0, []),
    "git.checkout_branch": ToolPolicy(True, 0, []),
    "git.create_branch": ToolPolicy(True, 0, []),
    "git.branch": ToolPolicy(True, 0, []),
}
