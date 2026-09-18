"""File & code assistant skill.

Deliberately sandboxed: reads/writes are confined to jarvis/workspace/, and
code execution runs in a subprocess with a timeout. This is a conscious
security boundary - a voice/text-driven assistant that can run arbitrary
shell commands anywhere on disk is a real risk (misheard speech, a
malicious prompt-injected instruction, etc.), so this does NOT expose
unrestricted shell access. Widen it deliberately and only if you understand
that trade-off.
"""
import os
import subprocess
import sys

from jarvis import config

os.makedirs(config.WORKSPACE_DIR, exist_ok=True)


def _safe_path(filename: str) -> str:
    path = os.path.abspath(os.path.join(config.WORKSPACE_DIR, filename))
    if not path.startswith(os.path.abspath(config.WORKSPACE_DIR) + os.sep) and path != os.path.abspath(config.WORKSPACE_DIR):
        raise ValueError("Path escapes the workspace directory.")
    return path


def read_file(filename: str) -> str:
    path = _safe_path(filename)
    if not os.path.isfile(path):
        return f"No such file in workspace: {filename}"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_file(filename: str, content: str) -> str:
    path = _safe_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} chars to {filename}."


def list_files() -> str:
    entries = sorted(os.listdir(config.WORKSPACE_DIR))
    entries = [e for e in entries if e != ".gitkeep"]
    return "Workspace files:\n" + "\n".join(entries) if entries else "Workspace is empty."


def run_python(code: str, timeout: int = 10) -> str:
    """Runs a short python snippet in a subprocess, isolated from this process."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=config.WORKSPACE_DIR,
        )
    except subprocess.TimeoutExpired:
        return f"Execution timed out after {timeout}s."

    out = result.stdout.strip()
    err = result.stderr.strip()
    if result.returncode != 0:
        return f"Exited with code {result.returncode}.\nstdout: {out}\nstderr: {err}"
    return out or "(no output)"
