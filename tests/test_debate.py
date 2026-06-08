from unittest.mock import MagicMock

from ai_debate.core.debate import DebateEngine
from ai_debate.core.gatekeeper import RateLimiter
from ai_debate.models.schemas import AgentTurn, JudgeScore

_GOOD_ARG = "word " * 90


def _make_turn(agent: str, round_num: int) -> AgentTurn:
    return AgentTurn(
        agent=agent,  # type: ignore[arg-type]
        round=round_num,
        role="debater",
        argument=_GOOD_ARG,
        word_count=90,
        format_valid=True,
    )


def _make_score(round_num: int) -> JudgeScore:
    return JudgeScore(
        round=round_num,
        ai_teacher_score=70,
        human_teacher_score=65,
        reasoning="AI argued more concisely.",
    )


def _build_engine(max_rounds: int = 10) -> DebateEngine:
    gatekeeper = RateLimiter(rpm=600)

    ai_agent = MagicMock()
    human_agent = MagicMock()
    judge = MagicMock()

    ai_agent.argue.side_effect = [_make_turn("AI_Teacher_Agent", i) for i in range(1, max_rounds + 1)]
    human_agent.argue.side_effect = [_make_turn("Human_Teacher_Agent", i) for i in range(1, max_rounds + 1)]
    judge.validate_response.return_value = True
    judge.score_round.side_effect = [_make_score(i) for i in range(1, max_rounds + 1)]
    judge.declare_winner.return_value = "AI_Teacher_Agent wins with 700 vs 650 points."

    return DebateEngine(judge=judge, ai_agent=ai_agent, human_agent=human_agent, gatekeeper=gatekeeper)


def test_full_debate_produces_20_turns():
    engine = _build_engine()
    transcript = engine.run()
    assert len(transcript.turns) == 20


def test_full_debate_produces_10_scores():
    engine = _build_engine()
    transcript = engine.run()
    assert len(transcript.scores) == 10


def test_full_debate_has_winner():
    engine = _build_engine()
    transcript = engine.run()
    assert transcript.winner is not None
    assert "wins" in transcript.winner


def test_agents_called_10_times_each():
    engine = _build_engine()
    engine.run()
    assert engine.ai_agent.argue.call_count == 10
    assert engine.human_agent.argue.call_count == 10


def test_judge_scores_10_rounds():
    engine = _build_engine()
    engine.run()
    assert engine.judge.score_round.call_count == 10
