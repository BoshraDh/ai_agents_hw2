from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


class AgentTurn(BaseModel):
    agent: Literal["AI_Teacher_Agent", "Human_Teacher_Agent", "Judge"]
    round: int
    role: Literal["debater", "judge"]
    argument: str | None = None
    round_summary: str | None = None
    final_verdict: str | None = None
    word_count: int
    format_valid: bool

    @field_validator("round")
    @classmethod
    def validate_round(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError(f"round must be 1–10, got {v}")
        return v

    @field_validator("word_count")
    @classmethod
    def validate_word_count(cls, v: int) -> int:
        if v < 0:
            raise ValueError("word_count cannot be negative")
        return v


class JudgeScore(BaseModel):
    round: int
    ai_teacher_score: int
    human_teacher_score: int
    reasoning: str

    @field_validator("ai_teacher_score", "human_teacher_score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError(f"score must be 0–100, got {v}")
        return v

    @field_validator("round")
    @classmethod
    def validate_round(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError(f"round must be 1–10, got {v}")
        return v


class DebateTranscript(BaseModel):
    topic: str
    turns: list[AgentTurn] = []
    scores: list[JudgeScore] = []
    winner: str | None = None
