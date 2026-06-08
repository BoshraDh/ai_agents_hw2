from __future__ import annotations

import json
import logging
import textwrap
from pathlib import Path

from ..agents.ai_teacher import AITeacherAgent
from ..agents.human_teacher import HumanTeacherAgent
from ..agents.judge import JudgeAgent
from ..core.gatekeeper import RateLimiter
from ..models.schemas import AgentTurn, DebateTranscript, JudgeScore
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
        Path("logs").mkdir(exist_ok=True)
        Path("logs/debate_transcript.json").write_text("[]", encoding="utf-8")
        print(f"\n{'=' * 60}\nDEBATE TOPIC:\n{TOPIC}\n{'=' * 60}")

        for round_num in range(1, settings.max_rounds + 1):
            print(format_round_header(round_num))
            ai_turn, human_turn = self._execute_round(round_num, transcript.turns)
            transcript.turns.extend([ai_turn, human_turn])

            score = self.judge.score_round(ai_turn, human_turn)
            transcript.scores.append(score)
            self._log_round(round_num, ai_turn, human_turn, score)
            print(f"  [Scores] AI: {score.ai_teacher_score:3d} | Human: {score.human_teacher_score:3d}")

        verdict = self.judge.declare_winner(transcript)
        transcript.winner = verdict
        print(f"\n{'=' * 60}\nFINAL VERDICT\n{'=' * 60}\n{verdict}\n{'=' * 60}\n")
        self._export_transcript(transcript)
        return transcript

    def _execute_round(self, round_num: int, context: list[AgentTurn]) -> tuple[AgentTurn, AgentTurn]:
        print(self.judge.introduce_agent("AI_Teacher_Agent", round_num))
        self.gatekeeper.acquire()
        ai_turn = self.ai_agent.argue(round_num, context)
        if not self.judge.validate_response(ai_turn):
            logger.warning(f"Round {round_num}: AI_Teacher_Agent response forfeited")
            ai_turn.format_valid = False
        self._print_turn("AI   ", ai_turn.argument)
        ai_fb = self.judge.interim_feedback("AI_Teacher_Agent", ai_turn.argument or "[FORFEITED]")
        print(self.judge.transition_to("AI_Teacher_Agent", "Human_Teacher_Agent", ai_fb))

        self.gatekeeper.acquire()
        human_turn = self.human_agent.argue(round_num, context)
        if not self.judge.validate_response(human_turn):
            logger.warning(f"Round {round_num}: Human_Teacher_Agent response forfeited")
            human_turn.format_valid = False
        self._print_turn("Human", human_turn.argument)
        human_fb = self.judge.interim_feedback("Human_Teacher_Agent", human_turn.argument or "[FORFEITED]")
        print(f"  [Judge] {human_fb}")

        return ai_turn, human_turn

    def _print_turn(self, label: str, text: str | None) -> None:
        content = text or "[FORFEITED]"
        prefix = f"  {label}: "
        indent = " " * len(prefix)
        print(textwrap.fill(content, width=100, initial_indent=prefix, subsequent_indent=indent))

    def _log_round(
        self, round_num: int, ai_turn: AgentTurn, human_turn: AgentTurn, score: JudgeScore
    ) -> None:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "debate_transcript.json"
        existing: list[dict] = []
        if log_file.exists():
            try:
                data = json.loads(log_file.read_text(encoding="utf-8"))
                existing = data if isinstance(data, list) else []
            except Exception:
                existing = []
        existing.append({
            "round": round_num,
            "ai_turn": ai_turn.model_dump(),
            "human_turn": human_turn.model_dump(),
            "judge_score": score.model_dump(),
        })
        log_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

    def _export_transcript(self, transcript: DebateTranscript) -> None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        out_file = output_dir / "transcript.json"
        out_file.write_text(transcript.model_dump_json(indent=2), encoding="utf-8")
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        full_log = logs_dir / "debate_transcript.json"
        full_log.write_text(transcript.model_dump_json(indent=2), encoding="utf-8")
        print(f"Transcript -> {out_file.resolve()}")
        print(f"Full log   -> {full_log.resolve()}")
