import json
from unittest.mock import MagicMock

from ai_debate.agents.ai_teacher import AITeacherAgent
from ai_debate.agents.human_teacher import HumanTeacherAgent
from ai_debate.models.schemas import AgentTurn

_GOOD_ARG = "word " * 90  # 90 words — within [80, 150]
_SHORT_ARG = "Too short."


def _mock_client(argument: str, agent: str, round_num: int) -> MagicMock:
    payload = {
        "agent": agent,
        "round": round_num,
        "role": "debater",
        "argument": argument,
        "round_summary": None,
        "final_verdict": None,
        "word_count": len(argument.split()),
        "format_valid": True,
    }
    client = MagicMock()
    client.ask.return_value = json.dumps(payload)
    return client


# ── AITeacherAgent ────────────────────────────────────────────────────────────

def test_ai_teacher_valid_turn():
    agent = AITeacherAgent(client=_mock_client(_GOOD_ARG, "AI_Teacher_Agent", 1))
    turn = agent.argue(1, [])
    assert isinstance(turn, AgentTurn)
    assert turn.agent == "AI_Teacher_Agent"
    assert turn.format_valid is True
    assert turn.argument is not None


def test_ai_teacher_retries_on_short_argument():
    good_json = json.dumps({"agent": "AI_Teacher_Agent", "round": 1, "role": "debater",
                            "argument": _GOOD_ARG, "round_summary": None, "final_verdict": None,
                            "word_count": 90, "format_valid": True})
    short_json = json.dumps({"agent": "AI_Teacher_Agent", "round": 1, "role": "debater",
                             "argument": _SHORT_ARG, "round_summary": None, "final_verdict": None,
                             "word_count": 2, "format_valid": True})
    client = MagicMock()
    client.ask.side_effect = [short_json, good_json]
    agent = AITeacherAgent(client=client)
    turn = agent.argue(1, [])
    assert client.ask.call_count == 2
    assert turn.format_valid is True


def test_ai_teacher_forfeits_after_two_failures():
    short_json = json.dumps({"agent": "AI_Teacher_Agent", "round": 1, "role": "debater",
                             "argument": _SHORT_ARG, "round_summary": None, "final_verdict": None,
                             "word_count": 2, "format_valid": True})
    client = MagicMock()
    client.ask.return_value = short_json
    agent = AITeacherAgent(client=client)
    turn = agent.argue(1, [])
    assert turn.format_valid is False


# ── HumanTeacherAgent ─────────────────────────────────────────────────────────

def test_human_teacher_valid_turn():
    agent = HumanTeacherAgent(client=_mock_client(_GOOD_ARG, "Human_Teacher_Agent", 1))
    turn = agent.argue(1, [])
    assert turn.agent == "Human_Teacher_Agent"
    assert turn.format_valid is True


def test_human_teacher_retries_on_short_argument():
    good_json = json.dumps({"agent": "Human_Teacher_Agent", "round": 2, "role": "debater",
                            "argument": _GOOD_ARG, "round_summary": None, "final_verdict": None,
                            "word_count": 90, "format_valid": True})
    short_json = json.dumps({"agent": "Human_Teacher_Agent", "round": 2, "role": "debater",
                             "argument": _SHORT_ARG, "round_summary": None, "final_verdict": None,
                             "word_count": 2, "format_valid": True})
    client = MagicMock()
    client.ask.side_effect = [short_json, good_json]
    agent = HumanTeacherAgent(client=client)
    turn = agent.argue(2, [])
    assert client.ask.call_count == 2
    assert turn.format_valid is True
