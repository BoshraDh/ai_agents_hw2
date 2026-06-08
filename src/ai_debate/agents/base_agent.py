from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod

import anthropic

from ..models.schemas import AgentTurn

logger = logging.getLogger("ai_debate")


class BaseDebateAgent(ABC):
    def __init__(self, name: str, position: str, client: anthropic.Anthropic) -> None:
        self.name = name
        self.position = position
        self.client = client

    @abstractmethod
    def argue(self, round_num: int, context: list[AgentTurn]) -> AgentTurn: ...

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def _validate_word_count(self, text: str) -> bool:
        from ..config import settings
        wc = self._count_words(text)
        return settings.min_words <= wc <= settings.max_words

    def _build_system_prompt(self) -> str:
        return (
            f"You are {self.name} in a formal academic debate.\n"
            f"Your position: {self.position}.\n"
            "Respond ONLY with a single valid JSON object — no extra text, no markdown fences."
        )

    def _parse_response(self, raw: str, round_num: int) -> AgentTurn:
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data = json.loads(raw)
            return AgentTurn.model_validate(data)
        except Exception as exc:
            logger.warning(f"{self.name} round {round_num} parse error: {exc}")
            return AgentTurn(
                agent=self.name,  # type: ignore[arg-type]
                round=round_num,
                role="debater",
                argument=None,
                word_count=0,
                format_valid=False,
            )
