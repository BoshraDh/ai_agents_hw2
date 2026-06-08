# Technical Architecture & Class Structure
# AI vs. Human Teachers — 3-Agent Debate System

**Version:** 1.2.0 | **Status:** Approved

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
    def __init__(self, client: CLIClient, gatekeeper: RateLimiter): ...
    def next_turn(self, round_num: int) -> str: ...              # alternating controller
    def validate_response(self, turn: AgentTurn) -> bool: ...
    def introduce_agent(self, agent_name: str, round_num: int) -> str: ...  # template intro
    def interim_feedback(self, agent_name: str, argument: str) -> str: ...  # CLI insight call
    def transition_to(self, from_agent: str, to_agent: str, feedback: str) -> str: ...
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
      Judge.introduce_agent("AI_Teacher_Agent", round)   → print "[Judge] Round N -- AI Teacher..."
        Gatekeeper.acquire()
          AI_Teacher_Agent.argue(round, context) → AgentTurn
            Judge.validate_response() → True | forfeit
          Judge.interim_feedback("AI_Teacher_Agent", argument)  → CLI call → insight string
          Judge.transition_to("AI_Teacher_Agent", "Human_Teacher_Agent", insight) → print
        Gatekeeper.acquire()
          Human_Teacher_Agent.argue(round, context) → AgentTurn
            Judge.validate_response() → True | forfeit
          Judge.interim_feedback("Human_Teacher_Agent", argument) → CLI call → insight string
          print "[Judge] {insight}"
      Judge.score_round(ai_turn, human_turn) → JudgeScore  [CLI call]
      print "[Scores] AI: N | Human: N"
 └─ Judge.declare_winner(transcript) → winner_name  [no ties]
```

---

## 4. Pydantic Validation Contract

All API responses are parsed via `AgentTurn.model_validate(json.loads(raw))`.  
`ValidationError` → round forfeited, that agent scores 0 for the round.  
Word-count range enforced via `@field_validator`; one automatic retry allowed.

---

## 6. Active Judge Moderation (v1.2)

### 6.1 Judge Introduction & Transition
- `introduce_agent(agent_name, round_num) -> str` — template string (no CLI call), printed
  before each agent speaks: *"[Judge] Round N -- [label], please present your argument."*
- `transition_to(from_agent, to_agent, feedback) -> str` — template string embedding the
  interim feedback: *"[Judge] {insight} -- Now, [next label], your response."*

### 6.2 Judge's Interim Feedback (per agent)
- `interim_feedback(agent_name, argument) -> str` — single CLI call after each agent argument
- System prompt `_INTERIM_SYSTEM`: *"one concise insight sentence, max 25 words, plain text"*
- Replaces the old "Round Summary" line (which was one call per round after both agents)

### 6.3 Display Flow (per round)
```
[Judge] Round N -- AI Teacher, please present your argument.
  AI   : [argument text, wrapped at 100 chars]
  [Judge] [AI insight] -- Now, Human Teacher, your response.
  Human: [argument text, wrapped at 100 chars]
  [Judge] [Human insight]
  [Scores] AI: NN | Human: NN
```

---

## 5. System Prompt & Display Refactor (v1.1)

### 5.1 Agent Word-Count Tightening
- `config.py`: `max_words` reduced from 150 → **120**
- Both agent system prompts updated with explicit penalty warning:
  `"Exceeding 120 words will result in a penalty from the Judge Agent."`
- Instruction added: *"Be direct and concise. Focus on density of information,
  not length. Avoid unnecessary filler phrases."*
- `_JSON_SCHEMA` in each agent updated to reflect 80–120 word constraint

### 5.2 Controller Display Refactor (`core/debate.py`)
- Replace `[:100]` hard truncation with `textwrap.fill()` (width=100)
- `_print_turn(label, text)` helper wraps full argument text with consistent
  indentation — no content is ever cut off in the terminal

---

## 5. File Line-Count Budget

| File                    | Budget  |
|-------------------------|---------|
| `main.py`               | ≤ 60    |
| `config.py`             | ≤ 50    |
| `models/schemas.py`     | ≤ 100   |
| `agents/base_agent.py`  | ≤ 80    |
| `agents/ai_teacher.py`  | ≤ 80    |
| `agents/human_teacher.py` | ≤ 80  |
| `agents/judge.py`       | ≤ 150   |
| `core/debate.py`        | ≤ 150   |
| `core/gatekeeper.py`    | ≤ 80    |
| `utils/helpers.py`      | ≤ 60    |
