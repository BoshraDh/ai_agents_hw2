# TODO — 3-Agent AI Debate System
# Implementation Checklist

**Status Key:** `[ ]` Pending · `[x]` Done

---

## 1. Project Setup & Environment

- [ ] Confirm `uv` is installed and `pyproject.toml` is configured
- [ ] Add all dependencies: `anthropic`, `pydantic`, `pydantic-settings`, `ruff`, `mypy`, `pytest`
- [ ] Create `.env` from `.env.example` and populate `ANTHROPIC_API_KEY`
- [ ] Configure `ruff` rules and `mypy` strict mode in `pyproject.toml`
- [ ] Create all `__init__.py` files under `src/ai_debate/` subtree
- [ ] Verify Python 3.12+ via `.python-version`

---

## 2. Core Models & Pydantic Schemas (`models/schemas.py`)

- [ ] Define `AgentTurn` with all required fields and `Literal` type constraints
- [ ] Add `@field_validator` — `word_count` must be in `[min_words, max_words]`
- [ ] Add `@field_validator` — `argument` must not be `None` when `role == "debater"`
- [ ] Add `@field_validator` — `round` must be in range `[1, 10]`
- [ ] Define `JudgeScore` model (per-round scores 0–100 + reasoning string)
- [ ] Define `DebateTranscript` model (topic, turns list, scores list, winner)
- [ ] Write `tests/test_schemas.py` — valid and invalid cases for all three models

---

## 3. Configuration Module (`config.py`)

- [ ] Implement `Settings(BaseSettings)` loading from `.env`
- [ ] Define typed fields: `anthropic_api_key`, `model`, `max_rounds`, `min_words`, `max_words`, `rate_limit_rpm`
- [ ] Export a module-level `settings = Settings()` singleton
- [ ] Verify missing `ANTHROPIC_API_KEY` raises a clear `ValidationError` at startup

---

## 4. Agent Definitions

### 4.1 Base Agent (`agents/base_agent.py`)

- [ ] Define `BaseDebateAgent(ABC)` with `name`, `position`, `client` fields
- [ ] Declare abstract `argue(round_num, context) -> AgentTurn`
- [ ] Implement `_count_words(text: str) -> int`
- [ ] Implement `_validate_word_count(text: str) -> bool`
- [ ] Implement `_build_system_prompt() -> str` — returns position-anchored prompt
- [ ] Implement `_parse_response(raw: str) -> AgentTurn` with `ValidationError` handling

### 4.2 AI Teacher Agent (`agents/ai_teacher.py`)

- [ ] Subclass `BaseDebateAgent` as `AITeacherAgent`
- [ ] Set `position` = "AI will completely replace human teachers"
- [ ] Define 5 required argument themes in system prompt (personalization, 24/7, analytics, equity, cost)
- [ ] Implement `argue(round_num, context) -> AgentTurn`
- [ ] Enforce word count `[80–150]`; automatically retry once if out of range

### 4.3 Human Teacher Agent (`agents/human_teacher.py`)

- [ ] Subclass `BaseDebateAgent` as `HumanTeacherAgent`
- [ ] Set `position` = "Human educators are irreplaceable"
- [ ] Define 5 required argument themes (empathy, mentorship, creativity, moral development, safeguarding)
- [ ] Implement `argue(round_num, context) -> AgentTurn`
- [ ] Enforce word count `[80–150]`; automatically retry once if out of range

---

## 5. Judge Agent (`agents/judge.py`)

- [ ] Implement `JudgeAgent` with injected `Anthropic` client and `RateLimiter`
- [ ] Implement `next_turn(round_num) -> str` — strict alternating order
- [ ] Implement `validate_response(turn: AgentTurn) -> bool` — schema + word count check
- [ ] Implement `score_round(ai_turn, human_turn) -> JudgeScore` — 5-criterion rubric (100 pts)
- [ ] Implement `declare_winner(transcript: DebateTranscript) -> str` — cumulative totals
- [ ] Add tie-breaking logic: if scores equal, winner decided by `reasoning` criterion sum

---

## 6. Gatekeeper / Rate Limiter (`core/gatekeeper.py`)

- [ ] Implement `RateLimiter` using token-bucket algorithm
- [ ] Initialize bucket capacity and refill rate from `settings.rate_limit_rpm`
- [ ] Implement `acquire()` — blocks with `time.sleep` until a token is available
- [ ] Implement `tokens_remaining() -> int`
- [ ] Log a warning when wait exceeds 5 seconds
- [ ] Write `tests/test_gatekeeper.py` — verify blocking and token refill behavior

---

## 7. Debate Engine (`core/debate.py`)

- [ ] Implement `DebateEngine` wiring `JudgeAgent`, both debaters, and `RateLimiter`
- [ ] Implement `run() -> DebateTranscript` — iterate rounds 1–10 strictly
- [ ] Implement `_execute_round(round_num) -> tuple[AgentTurn, AgentTurn]`
- [ ] Handle forfeited rounds (invalid response) — log warning, assign score 0
- [ ] Implement `_export_transcript(t)` — write `output/transcript.json` after round 10
- [ ] Print round-by-round summary to stdout during execution

---

## 8. Utils (`utils/helpers.py`)

- [ ] Implement `count_words(text: str) -> int`
- [ ] Implement `truncate_context(turns: list, max_turns: int) -> list`
- [ ] Implement `format_round_header(round_num: int) -> str`
- [ ] Configure module-level `logger = logging.getLogger("ai_debate")`

---

## 9. Main Entry Point (`main.py`)

- [ ] Instantiate `Settings`, `Anthropic` client, `RateLimiter`, all agents, `DebateEngine`
- [ ] Call `DebateEngine.run()` and print the final verdict to stdout
- [ ] Handle `KeyboardInterrupt` — print partial transcript before exit
- [ ] Handle `anthropic.APIError` — log message and exit with code 1

---

## 10. Validation, Error Handling & Edge Cases

- [ ] Agent returns invalid JSON → forfeit round, score = 0, continue
- [ ] Agent exceeds word count after retry → apply –10 pt format penalty
- [ ] All 20 pings must fire — no early termination under any condition
- [ ] Confirm tie is mathematically impossible given 5-criterion scoring rules

---

## 11. Testing

- [ ] `tests/test_schemas.py` — valid/invalid `AgentTurn`, `JudgeScore`, `DebateTranscript`
- [ ] `tests/test_agents.py` — mock API, verify retry and word-count enforcement
- [ ] `tests/test_gatekeeper.py` — token-bucket blocks and releases correctly
- [ ] `tests/test_debate.py` — full 2-round smoke test with mocked agents
- [ ] Run `pytest --tb=short` — all tests green
- [ ] Run `ruff check src/` and `mypy src/` — zero errors
