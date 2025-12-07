"""
Rich-based UI helpers for v-shell CLI.

Provides status indicators, spinners, and formatted output rendering.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live
from contextlib import contextmanager
from typing import Optional

console = Console()


def show_status(message: str, style: str = "bold cyan") -> None:
    """Display a status message with color."""
    console.print(f"[{style}]{message}[/]")


def show_error(message: str) -> None:
    """Display an error message."""
    console.print(f"[bold red]Error:[/] {message}")


def show_success(message: str) -> None:
    """Display a success message."""
    console.print(f"[bold green]{message}[/]")


def show_panel(title: str, body: str, border_style: str = "cyan") -> None:
    """Display content in a Rich panel."""
    console.print(Panel.fit(body, title=title, border_style=border_style))


@contextmanager
def spinner(message: str):
    """Context manager for displaying a spinner during async operations."""
    with Live(Spinner("dots", text=f"[dim]{message}[/]"), refresh_per_second=10, console=console):
        yield


def render_git_status(raw: str) -> None:
    """
    Render git status output as a Rich table.
    
    Parses the output and displays:
    - Branch info in a panel
    - Changed files in a table (all files, no truncation)
    """
    lines = raw.strip().splitlines()
    if not lines:
        show_panel("Git Status", "[dim]No output[/]")
        return

    # Extract branch info (usually first line)
    branch_info = lines[0] if lines else "Unknown branch"
    
    # Parse file changes (all lines after the first)
    file_lines = lines[1:]
    
    # Display branch info
    console.print(Panel.fit(branch_info, title="[bold green]Branch[/]", border_style="green"))
    
    if not file_lines:
        console.print("[dim]Working tree clean[/]")
        return
    
    # Create table for file changes
    table = Table(show_header=True, header_style="bold magenta", border_style="dim", box=None)
    table.add_column("Status", style="yellow", width=15, no_wrap=True)
    table.add_column("File", style="cyan", no_wrap=True)

    # Parse each file line
    for line in file_lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse git status -sb format: "XY filename"
        # First 2 chars are status, rest is filename
        if len(line) >= 3:
            status = line[:2]
            filepath = line[3:] if len(line) > 3 else line[2:]
            
            # Map status codes to readable names with icons
            status_map = {
                ' M': '📝 Modified',
                'M ': '📝 Modified',
                'MM': '📝 Modified',
                'A ': '➕ Added',
                'AM': '➕ Added',
                'D ': '❌ Deleted',
                '??': '❓ Untracked',
                'R ': '🔄 Renamed',
                'C ': '📋 Copied',
                'U ': '⚠️ Conflict',
            }
            status_display = status_map.get(status, status)
            
            table.add_row(status_display, filepath)

    # Display table
    if table.row_count > 0:
        console.print(table)
    else:
        console.print("[dim]Working tree clean[/]")


def render_simple_block(title: str, raw: str, border_style: str = "cyan") -> None:
    """Render a simple text block in a Rich panel."""
    body = raw.strip() or "[dim]No output[/]"
    show_panel(title, body, border_style=border_style)


def render_git_log(raw: str) -> None:
    """Render git log output in a formatted panel."""
    render_simple_block("📜 Git Log", raw, border_style="blue")


def render_git_diff(raw: str) -> None:
    """Render git diff output in a formatted panel."""
    render_simple_block("📊 Git Diff", raw, border_style="yellow")


def render_test_results(summary: str, output: str) -> None:
    """Render test results with summary and output."""
    combined = f"[bold]{summary}[/]\n\n{output.strip()}"
    render_simple_block("🧪 Test Results", combined, border_style="magenta")


def render_smart_commit(result: dict) -> None:
    """
    Render smart commit push output with multiple panels.
    
    Shows:
    - Git status
    - Commit message
    - Commit output
    - Push output
    """
    status_text = result.get("status", "")
    commit_msg = result.get("commit_message", "")
    commit_out = result.get("commit_stdout", "")
    push_out = result.get("push_stdout", "")
    
    if status_text:
        render_git_status(status_text)
    
    if commit_msg:
        render_simple_block("💬 Commit Message", commit_msg, border_style="green")
    
    if commit_out:
        render_simple_block("✅ Git Commit", commit_out, border_style="green")
    
    if push_out:
        render_simple_block("🚀 Git Push", push_out, border_style="blue")
