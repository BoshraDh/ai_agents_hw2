from __future__ import annotations

import json
import logging

import anthropic
from anthropic.types import MessageParam, TextBlock

from ..core.gatekeeper import RateLimiter
from ..models.schemas import AgentTurn, DebateTranscript, JudgeScore

logger = logging.getLogger("ai_debate")

_SCORE_SYSTEM = """You are the objective Judge in an AI vs. Human Teachers debate.
Score each argument pair using these 5 criteria (total 100 pts per agent):
  - Logical reasoning depth:   30 pts
  - Evidence quality:          25 pts
  - Relevance to topic:        20 pts
  - Format/schema compliance:  15 pts
  - Word count adherence:      10 pts
Respond ONLY with JSON (no markdown):
{"round":<n>,"ai_teacher_score":<0-100>,"human_teacher_score":<0-100>,"reasoning":"<1 sentence>"}"""

_VERDICT_SYSTEM = """You are the Judge. Declare one winner — ties are NOT permitted.
If cumulative scores are equal, the agent with the higher total reasoning-depth criterion wins.
Respond ONLY with JSON (no markdown):
{"agent":"Judge","round":10,"role":"judge","argument":null,"round_summary":null,
 "final_verdict":"<100-200 words: name winner, cite score differential, reference 2 deciding rounds>",
 "word_count":<n>,"format_valid":true}"""


class JudgeAgent:
    _TURN_ORDER = ["AI_Teacher_Agent", "Human_Teacher_Agent"]

    def __init__(self, client: anthropic.Anthropic, gatekeeper: RateLimiter) -> None:
        self.client = client
        self.gatekeeper = gatekeeper

    def next_turn(self, round_num: int) -> str:
        return self._TURN_ORDER[(round_num - 1) % 2]

    def validate_response(self, turn: AgentTurn) -> bool:
        from ..config import settings

        if not turn.format_valid:
            return False
        if turn.role == "debater" and not turn.argument:
            return False
        if turn.argument:
            wc = len(turn.argument.split())
            if not (settings.min_words <= wc <= settings.max_words):
                logger.warning(
                    f"{turn.agent} round {turn.round}: word count {wc} outside [{settings.min_words},{settings.max_words}]"
                )
                return False
        return True

    def score_round(self, ai_turn: AgentTurn, human_turn: AgentTurn) -> JudgeScore:
        from ..config import settings

        self.gatekeeper.acquire()
        prompt = (
            f"Round {ai_turn.round}\n"
            f"AI_Teacher_Agent argument: {ai_turn.argument or '[FORFEITED]'}\n"
            f"Human_Teacher_Agent argument: {human_turn.argument or '[FORFEITED]'}\n"
            "Score both agents now."
        )
        response = self.client.messages.create(
            model=settings.model,
            max_tokens=256,
            system=_SCORE_SYSTEM,
            messages=[MessageParam(role="user", content=prompt)],
        )
        raw_text = next((b.text for b in response.content if isinstance(b, TextBlock)), "")
        raw = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return JudgeScore.model_validate(json.loads(raw))
        except Exception:
            ai_pts = 0 if not ai_turn.argument else 50
            human_pts = 0 if not human_turn.argument else 50
            return JudgeScore(round=ai_turn.round, ai_teacher_score=ai_pts, human_teacher_score=human_pts, reasoning="Parse error — defaults applied")

    def declare_winner(self, transcript: DebateTranscript) -> str:
        from ..config import settings

        ai_total = sum(s.ai_teacher_score for s in transcript.scores)
        human_total = sum(s.human_teacher_score for s in transcript.scores)
        breakdown = "\n".join(
            f"Round {s.round}: AI={s.ai_teacher_score} Human={s.human_teacher_score} — {s.reasoning}"
            for s in transcript.scores
        )
        self.gatekeeper.acquire()
        response = self.client.messages.create(
            model=settings.model,
            max_tokens=512,
            system=_VERDICT_SYSTEM,
            messages=[MessageParam(role="user", content=(
                f"AI_Teacher_Agent cumulative: {ai_total}\n"
                f"Human_Teacher_Agent cumulative: {human_total}\n"
                f"Per-round breakdown:\n{breakdown}\nDeclare the winner now."
            ))],
        )
        raw_text2 = next((b.text for b in response.content if isinstance(b, TextBlock)), "")
        raw = raw_text2.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data = json.loads(raw)
            turn = AgentTurn.model_validate(data)
            return turn.final_verdict or f"Winner: {'AI_Teacher_Agent' if ai_total >= human_total else 'Human_Teacher_Agent'}"
        except Exception:
            winner = "AI_Teacher_Agent" if ai_total >= human_total else "Human_Teacher_Agent"
            return f"{winner} wins — {max(ai_total, human_total)} vs {min(ai_total, human_total)} points."
