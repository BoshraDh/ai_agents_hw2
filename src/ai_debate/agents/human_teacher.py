from __future__ import annotations

import logging

import anthropic
from anthropic.types import MessageParam, TextBlock

from ..models.schemas import AgentTurn
from ..utils.helpers import truncate_context
from .base_agent import BaseDebateAgent

logger = logging.getLogger("ai_debate")

_THEMES = """
Key argument themes to develop across rounds:
1. Emotional intelligence and empathetic mentorship
2. Social and moral development beyond curriculum
3. Spontaneous creativity and contextual adaptability
4. Role modeling, inspiration, and nurturing intrinsic motivation
5. Ethical oversight and safeguarding responsibilities
"""

_JSON_SCHEMA = (
    '{"agent":"Human_Teacher_Agent","round":<n>,"role":"debater",'
    '"argument":"<your 80-150 word argument here>","round_summary":null,'
    '"final_verdict":null,"word_count":<n>,"format_valid":true}'
)


class HumanTeacherAgent(BaseDebateAgent):
    def __init__(self, client: anthropic.Anthropic) -> None:
        super().__init__(
            name="Human_Teacher_Agent",
            position="Human educators are irreplaceable — empathy, mentorship, and soul",
            client=client,
        )

    def argue(self, round_num: int, context: list[AgentTurn]) -> AgentTurn:
        from ..config import settings

        system = self._build_system_prompt() + _THEMES + f"\nRespond ONLY with JSON:\n{_JSON_SCHEMA}"
        messages = self._build_messages(round_num, context)

        for attempt in range(2):
            response = self.client.messages.create(
                model=settings.model,
                max_tokens=512,
                system=system,
                messages=messages,
            )
            raw = next((b.text for b in response.content if isinstance(b, TextBlock)), "")
            turn = self._parse_response(raw, round_num)
            if turn.format_valid and turn.argument and self._validate_word_count(turn.argument):
                turn.word_count = self._count_words(turn.argument)
                return turn
            logger.warning(f"HumanTeacherAgent attempt {attempt + 1} failed word-count check — retrying")

        turn.format_valid = False
        return turn

    def _build_messages(self, round_num: int, context: list[AgentTurn]) -> list[MessageParam]:
        recent = truncate_context(context, 6)
        history = "\n".join(
            f"Round {t.round} [{t.agent}]: {t.argument or t.round_summary or '[no content]'}"
            for t in recent
        )
        content = f"Round {round_num} of 10.\nDebate history:\n{history}\n\nMake your argument now."
        return [{"role": "user", "content": content}]
