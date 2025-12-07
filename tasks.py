import subprocess
import sys

def _run(cmd: str) -> int:
    print(f"$ {cmd}")
    return subprocess.call(cmd, shell=True)

def dev() -> int:
    return _run("python -m app.main")

def mcp() -> int:
    return _run("python -m app.mcp.server")

def test() -> int:
    return _run("python -m pytest")

def lint() -> int:
    return _run("python -m ruff check app tests")

def format() -> int:
    return _run("python -m ruff format app tests")

if __name__ == "__main__":
    # simple CLI: python tasks.py dev|mcp|test
    if len(sys.argv) < 2:
        print("Usage: python tasks.py [dev|mcp|test|lint|format]")
        print("Commands:")
        print("  dev    - Run the voice CLI")
        print("  mcp    - Run the MCP server")
        print("  test   - Run tests")
        print("  lint   - Lint code with ruff")
        print("  format - Format code with ruff")
        sys.exit(1)
    
    cmd_name = sys.argv[1]
    if cmd_name in globals():
        sys.exit(globals()[cmd_name]())
    else:
        print(f"Unknown command: {cmd_name}")
        sys.exit(1)
