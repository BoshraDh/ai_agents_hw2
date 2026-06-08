from __future__ import annotations

import logging
import shutil
import subprocess

logger = logging.getLogger("ai_debate")


class CLIClient:
    """Calls the authenticated 'claude' CLI as a subprocess — no API key required."""

    def __init__(self) -> None:
        if not shutil.which("claude"):
            raise RuntimeError(
                "'claude' CLI not found in PATH. "
                "Make sure Claude Code is installed and 'claude' is on your PATH."
            )

    def ask(self, system: str, user: str, timeout: int = 120) -> str:
        prompt = f"{system}\n\n---\n\n{user}"
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            logger.warning(f"claude CLI non-zero exit: {result.stderr[:300]}")
        return result.stdout.strip()
