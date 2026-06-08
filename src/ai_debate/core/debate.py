from __future__ import annotations

import logging
from pathlib import Path

from ..agents.ai_teacher import AITeacherAgent
from ..agents.human_teacher import HumanTeacherAgent
from ..agents.judge import JudgeAgent
from ..core.gatekeeper import RateLimiter
from ..models.schemas import AgentTurn, DebateTranscript
from ..utils.helpers import format_round_header

logger = logging.getLogger("ai_debate")

TOPIC = (
    "AI vs. Human Teachers: Will AI completely replace human teachers within a few years "
    "to deliver more effective education, or is the human element irreplaceable?"
)


class DebateEngine:
    def __init__(
        self,
        judge: JudgeAgent,
        ai_agent: AITeacherAgent,
        human_agent: HumanTeacherAgent,
        gatekeeper: RateLimiter,
    ) -> None:
        self.judge = judge
        self.ai_agent = ai_agent
        self.human_agent = human_agent
        self.gatekeeper = gatekeeper

    def run(self) -> DebateTranscript:
        from ..config import settings

        transcript = DebateTranscript(topic=TOPIC)
        print(f"\n{'=' * 60}\nDEBATE TOPIC: {TOPIC}\n{'=' * 60}")

        for round_num in range(1, settings.max_rounds + 1):
            print(format_round_header(round_num))
            ai_turn, human_turn = self._execute_round(round_num, transcript.turns)
            transcript.turns.extend([ai_turn, human_turn])

            score = self.judge.score_round(ai_turn, human_turn)
            transcript.scores.append(score)
            print(
                f"  Scores — AI: {score.ai_teacher_score:3d} | Human: {score.human_teacher_score:3d}\n"
                f"  Judge: {score.reasoning}"
            )

        verdict = self.judge.declare_winner(transcript)
        transcript.winner = verdict
        print(f"\n{'=' * 60}\nFINAL VERDICT\n{'=' * 60}\n{verdict}\n")
        self._export_transcript(transcript)
        return transcript

    def _execute_round(self, round_num: int, context: list[AgentTurn]) -> tuple[AgentTurn, AgentTurn]:
        self.gatekeeper.acquire()
        ai_turn = self.ai_agent.argue(round_num, context)
        if not self.judge.validate_response(ai_turn):
            logger.warning(f"Round {round_num}: AI_Teacher_Agent response forfeited")
            ai_turn.format_valid = False

        self.gatekeeper.acquire()
        human_turn = self.human_agent.argue(round_num, context)
        if not self.judge.validate_response(human_turn):
            logger.warning(f"Round {round_num}: Human_Teacher_Agent response forfeited")
            human_turn.format_valid = False

        ai_preview = (ai_turn.argument or "[FORFEITED]")[:100]
        human_preview = (human_turn.argument or "[FORFEITED]")[:100]
        print(f"  AI    : {ai_preview}...")
        print(f"  Human : {human_preview}...")
        return ai_turn, human_turn

    def _export_transcript(self, transcript: DebateTranscript) -> None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        out_file = output_dir / "transcript.json"
        out_file.write_text(transcript.model_dump_json(indent=2), encoding="utf-8")
        print(f"Transcript exported → {out_file.resolve()}")
