from __future__ import annotations

import logging

logger = logging.getLogger("ai_debate")


def count_words(text: str) -> int:
    return len(text.split())


def truncate_context(turns: list, max_turns: int) -> list:
    return turns[-max_turns:] if len(turns) > max_turns else turns


def format_round_header(round_num: int) -> str:
    return f"\n-- Round {round_num:02d} {'-' * 48}"
