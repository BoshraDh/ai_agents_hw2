import pytest
from pydantic import ValidationError

from ai_debate.models.schemas import AgentTurn, DebateTranscript, JudgeScore


def _turn(**overrides):
    base = dict(
        agent="AI_Teacher_Agent",
        round=1,
        role="debater",
        argument="word " * 90,
        word_count=90,
        format_valid=True,
    )
    base.update(overrides)
    return AgentTurn(**base)


# ── AgentTurn ──────────────────────────────────────────────────────────────────

def test_valid_agent_turn():
    t = _turn()
    assert t.agent == "AI_Teacher_Agent"
    assert t.format_valid is True


def test_invalid_agent_name():
    with pytest.raises(ValidationError):
        _turn(agent="InvalidAgent")


def test_round_too_low():
    with pytest.raises(ValidationError):
        _turn(round=0)


def test_round_too_high():
    with pytest.raises(ValidationError):
        _turn(round=11)


def test_invalid_role():
    with pytest.raises(ValidationError):
        _turn(role="referee")


def test_negative_word_count():
    with pytest.raises(ValidationError):
        _turn(word_count=-1)


def test_null_argument_allowed():
    t = _turn(argument=None, word_count=0, format_valid=False)
    assert t.argument is None


# ── JudgeScore ────────────────────────────────────────────────────────────────

def test_valid_judge_score():
    s = JudgeScore(round=3, ai_teacher_score=75, human_teacher_score=60, reasoning="AI was clearer")
    assert s.ai_teacher_score == 75


def test_score_above_100():
    with pytest.raises(ValidationError):
        JudgeScore(round=1, ai_teacher_score=101, human_teacher_score=50, reasoning="x")


def test_score_below_0():
    with pytest.raises(ValidationError):
        JudgeScore(round=1, ai_teacher_score=50, human_teacher_score=-1, reasoning="x")


def test_judge_score_round_out_of_range():
    with pytest.raises(ValidationError):
        JudgeScore(round=11, ai_teacher_score=50, human_teacher_score=50, reasoning="x")


# ── DebateTranscript ──────────────────────────────────────────────────────────

def test_transcript_defaults():
    t = DebateTranscript(topic="Test topic")
    assert t.turns == []
    assert t.scores == []
    assert t.winner is None


def test_transcript_with_turns():
    turn = _turn()
    t = DebateTranscript(topic="Test", turns=[turn])
    assert len(t.turns) == 1
