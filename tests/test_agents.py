import json
from unittest.mock import MagicMock

from anthropic.types import TextBlock

from ai_debate.agents.ai_teacher import AITeacherAgent
from ai_debate.agents.human_teacher import HumanTeacherAgent
from ai_debate.models.schemas import AgentTurn

_GOOD_ARG = "word " * 90  # 90 words — within [80, 150]
_SHORT_ARG = "Too short."


def _mock_response(agent: str, round_num: int, argument: str) -> MagicMock:
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
    msg = MagicMock()
    msg.content = [TextBlock(type="text", text=json.dumps(payload))]
    return msg


# ── AITeacherAgent ────────────────────────────────────────────────────────────

def test_ai_teacher_valid_turn():
    client = MagicMock()
    client.messages.create.return_value = _mock_response("AI_Teacher_Agent", 1, _GOOD_ARG)
    agent = AITeacherAgent(client=client)
    turn = agent.argue(1, [])
    assert isinstance(turn, AgentTurn)
    assert turn.agent == "AI_Teacher_Agent"
    assert turn.format_valid is True
    assert turn.argument is not None


def test_ai_teacher_retries_on_short_argument():
    client = MagicMock()
    client.messages.create.side_effect = [
        _mock_response("AI_Teacher_Agent", 1, _SHORT_ARG),
        _mock_response("AI_Teacher_Agent", 1, _GOOD_ARG),
    ]
    agent = AITeacherAgent(client=client)
    turn = agent.argue(1, [])
    assert client.messages.create.call_count == 2
    assert turn.format_valid is True


def test_ai_teacher_forfeits_after_two_failures():
    client = MagicMock()
    client.messages.create.side_effect = [
        _mock_response("AI_Teacher_Agent", 1, _SHORT_ARG),
        _mock_response("AI_Teacher_Agent", 1, _SHORT_ARG),
    ]
    agent = AITeacherAgent(client=client)
    turn = agent.argue(1, [])
    assert turn.format_valid is False


# ── HumanTeacherAgent ─────────────────────────────────────────────────────────

def test_human_teacher_valid_turn():
    client = MagicMock()
    client.messages.create.return_value = _mock_response("Human_Teacher_Agent", 1, _GOOD_ARG)
    agent = HumanTeacherAgent(client=client)
    turn = agent.argue(1, [])
    assert turn.agent == "Human_Teacher_Agent"
    assert turn.format_valid is True


def test_human_teacher_retries_on_short_argument():
    client = MagicMock()
    client.messages.create.side_effect = [
        _mock_response("Human_Teacher_Agent", 2, _SHORT_ARG),
        _mock_response("Human_Teacher_Agent", 2, _GOOD_ARG),
    ]
    agent = HumanTeacherAgent(client=client)
    turn = agent.argue(2, [])
    assert client.messages.create.call_count == 2
    assert turn.format_valid is True
