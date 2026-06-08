from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod

from ..core.cli_client import CLIClient
from ..core.gatekeeper import RateLimiter
from ..models.schemas import AgentTurn
from ..utils.helpers import count_words

logger = logging.getLogger("ai_debate")


class BaseDebateAgent(ABC):
    def __init__(
        self,
        name: str,
        position: str,
        client: CLIClient,
        gatekeeper: RateLimiter | None = None,
    ) -> None:
        self.name = name
        self.position = position
        self.client = client
        self.gatekeeper = gatekeeper

    @abstractmethod
    def argue(self, round_num: int, context: list[AgentTurn]) -> AgentTurn: ...

    def _acquire(self) -> None:
        if self.gatekeeper:
            self.gatekeeper.acquire()

    def _count_words(self, text: str) -> int:
        return count_words(text)

    def _validate_word_count(self, text: str) -> bool:
        from ..config import settings
        wc = self._count_words(text)
        return settings.min_words <= wc <= settings.max_words

    def _build_system_prompt(self) -> str:
        return (
            f"You are {self.name} in a formal academic debate.\n"
            f"Your position: {self.position}.\n"
            "You have access to web search — use it to find recent statistics and evidence.\n"
            "Respond ONLY with a single valid JSON object — no extra text, no markdown fences."
        )

    def _parse_response(self, raw: str, round_num: int) -> AgentTurn:
        """Parse raw CLI response into AgentTurn; returns forfeited turn on error."""
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return AgentTurn.model_validate(json.loads(raw))
        except Exception as exc:
            logger.warning(f"{self.name} round {round_num} parse error: {exc}")
            return AgentTurn(
                agent=self.name,  # type: ignore[arg-type]
                round=round_num,
                role="debater",
                argument="[FORFEITED]",
                word_count=0,
                format_valid=False,
            )
