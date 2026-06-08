from __future__ import annotations

import logging

from ..core.cli_client import CLIClient
from ..models.schemas import AgentTurn
from ..utils.helpers import truncate_context
from .base_agent import BaseDebateAgent

logger = logging.getLogger("ai_debate")

_THEMES = """
Key argument themes to develop across rounds:
1. Hyper-personalized adaptive learning paths
2. 24/7 availability and unlimited global scalability
3. Real-time performance analytics and learning-gap detection
4. Bias-free, consistent curriculum delivery
5. Cost reduction and worldwide education access equity
"""

_JSON_SCHEMA = (
    '{"agent":"AI_Teacher_Agent","round":<n>,"role":"debater",'
    '"argument":"<your 80-150 word argument>","round_summary":null,'
    '"final_verdict":null,"word_count":<n>,"format_valid":true}'
)


class AITeacherAgent(BaseDebateAgent):
    def __init__(self, client: CLIClient) -> None:
        super().__init__(
            name="AI_Teacher_Agent",
            position="AI will completely replace human teachers within a few years",
            client=client,
        )

    def argue(self, round_num: int, context: list[AgentTurn]) -> AgentTurn:
        system = self._build_system_prompt() + _THEMES + f"\nRespond ONLY with JSON:\n{_JSON_SCHEMA}"
        user = self._build_user_message(round_num, context)

        for attempt in range(2):
            raw = self.client.ask(system=system, user=user)
            turn = self._parse_response(raw, round_num)
            if turn.format_valid and turn.argument and self._validate_word_count(turn.argument):
                turn.word_count = self._count_words(turn.argument)
                return turn
            logger.warning(f"AITeacherAgent attempt {attempt + 1} failed word-count check — retrying")

        turn.format_valid = False
        return turn

    def _build_user_message(self, round_num: int, context: list[AgentTurn]) -> str:
        recent = truncate_context(context, 6)
        history = "\n".join(
            f"Round {t.round} [{t.agent}]: {t.argument or t.round_summary or '[no content]'}"
            for t in recent
        )
        return f"Round {round_num} of 10.\nDebate history:\n{history}\n\nMake your argument now."
