# Technical Architecture & Class Structure
# AI vs. Human Teachers — 3-Agent Debate System

**Version:** 1.0.0 | **Status:** Approved

---

## 1. Module Map

```
ai_agents_hw2/
├── docs/                          # PRD.md · PLAN.md · TODO.md
├── src/
│   └── ai_debate/
│       ├── __init__.py
│       ├── main.py                # Entry point            (≤ 60 lines)
│       ├── config.py              # Settings & env vars    (≤ 50 lines)
│       ├── models/
│       │   └── schemas.py         # Pydantic contracts     (≤ 100 lines)
│       ├── agents/
│       │   ├── base_agent.py      # Abstract base          (≤ 60 lines)
│       │   ├── ai_teacher.py      # Pro-AI debater         (≤ 80 lines)
│       │   ├── human_teacher.py   # Pro-human debater      (≤ 80 lines)
│       │   └── judge.py           # Orchestrator/arbiter   (≤ 150 lines)
│       ├── core/
│       │   ├── debate.py          # Turn-loop engine       (≤ 120 lines)
│       │   └── gatekeeper.py      # Rate limiter           (≤ 80 lines)
│       └── utils/
│           └── helpers.py         # Word count · logging   (≤ 60 lines)
├── tests/
│   ├── test_schemas.py
│   ├── test_agents.py
│   ├── test_gatekeeper.py
│   └── test_debate.py
├── pyproject.toml
└── .env.example
```

---

## 2. Class Responsibilities

### `config.py`
```python
class Settings(BaseSettings):
    anthropic_api_key: str
    model: str = "claude-sonnet-4-6"
    max_rounds: int = 10
    min_words: int = 80
    max_words: int = 150
    rate_limit_rpm: int = 10
    model_config = SettingsConfigDict(env_file=".env")
```

### `models/schemas.py`
```python
class AgentTurn(BaseModel):
    agent: Literal["AI_Teacher_Agent", "Human_Teacher_Agent", "Judge"]
    round: int                        # 1–10
    role: Literal["debater", "judge"]
    argument: str | None = None       # debater turns only
    round_summary: str | None = None  # judge turns only
    final_verdict: str | None = None  # round 10 judge only
    word_count: int
    format_valid: bool

class JudgeScore(BaseModel):
    round: int
    ai_teacher_score: int             # 0–100
    human_teacher_score: int          # 0–100
    reasoning: str

class DebateTranscript(BaseModel):
    topic: str
    turns: list[AgentTurn]
    scores: list[JudgeScore]
    winner: str | None = None
```

### `agents/base_agent.py`
```python
class BaseDebateAgent(ABC):
    def __init__(self, name: str, position: str, client: Anthropic): ...
    @abstractmethod
    def argue(self, round_num: int, context: list[AgentTurn]) -> AgentTurn: ...
    def _validate_word_count(self, text: str) -> bool: ...
    def _build_system_prompt(self) -> str: ...
    def _parse_response(self, raw: str) -> AgentTurn: ...
```

### `agents/judge.py`
```python
class JudgeAgent:
    def __init__(self, client: Anthropic, gatekeeper: RateLimiter): ...
    def next_turn(self, round_num: int) -> str: ...          # alternating controller
    def validate_response(self, turn: AgentTurn) -> bool: ...
    def score_round(self, ai: AgentTurn, human: AgentTurn) -> JudgeScore: ...
    def declare_winner(self, transcript: DebateTranscript) -> str: ...
```

### `core/gatekeeper.py`
```python
class RateLimiter:
    def __init__(self, rpm: int = 10): ...  # token-bucket algorithm
    def acquire(self) -> None: ...           # blocks until token available
    def release(self) -> None: ...
    def tokens_remaining(self) -> int: ...
```

### `core/debate.py`
```python
class DebateEngine:
    def __init__(self, judge, ai_agent, human_agent, gatekeeper): ...
    def run(self) -> DebateTranscript: ...                             # main loop
    def _execute_round(self, n: int) -> tuple[AgentTurn, AgentTurn]: ...
    def _export_transcript(self, t: DebateTranscript) -> None: ...
```

---

## 3. Turn-Taking Loop

```
DebateEngine.run()
 └─ for round in 1..10:
      Judge.next_turn(round) → "AI_Teacher_Agent"
        Gatekeeper.acquire()
          AI_Teacher_Agent.argue(round, context) → AgentTurn
            Judge.validate_response() → True | forfeit
      Judge.next_turn(round) → "Human_Teacher_Agent"
        Gatekeeper.acquire()
          Human_Teacher_Agent.argue(round, context) → AgentTurn
            Judge.validate_response() → True | forfeit
      Judge.score_round(ai_turn, human_turn) → JudgeScore
 └─ Judge.declare_winner(transcript) → winner_name  [no ties]
```

---

## 4. Pydantic Validation Contract

All API responses are parsed via `AgentTurn.model_validate(json.loads(raw))`.  
`ValidationError` → round forfeited, that agent scores 0 for the round.  
Word-count range enforced via `@field_validator`; one automatic retry allowed.

---

## 5. File Line-Count Budget

| File                    | Budget  |
|-------------------------|---------|
| `main.py`               | ≤ 60    |
| `config.py`             | ≤ 50    |
| `models/schemas.py`     | ≤ 100   |
| `agents/base_agent.py`  | ≤ 60    |
| `agents/ai_teacher.py`  | ≤ 80    |
| `agents/human_teacher.py` | ≤ 80  |
| `agents/judge.py`       | ≤ 150   |
| `core/debate.py`        | ≤ 120   |
| `core/gatekeeper.py`    | ≤ 80    |
| `utils/helpers.py`      | ≤ 60    |
