# TODO — 3-Agent AI Debate System
# Implementation Checklist

**Status Key:** `[ ]` Pending · `[x]` Done

---

## 1. Project Setup & Environment

- [x] Confirm `uv` is installed and `pyproject.toml` is configured
- [x] Add all dependencies: `anthropic`, `pydantic`, `pydantic-settings`, `ruff`, `mypy`, `pytest`
- [x] Create `.env` from `.env.example` and populate `ANTHROPIC_API_KEY`
- [x] Configure `ruff` rules and `mypy` strict mode in `pyproject.toml`
- [x] Create all `__init__.py` files under `src/ai_debate/` subtree
- [x] Verify Python 3.12+ via `.python-version`

---

## 2. Core Models & Pydantic Schemas (`models/schemas.py`)

- [x] Define `AgentTurn` with all required fields and `Literal` type constraints
- [x] Add `@field_validator` — `word_count` must be in `[min_words, max_words]`
- [x] Add `@field_validator` — `argument` must not be `None` when `role == "debater"`
- [x] Add `@field_validator` — `round` must be in range `[1, 10]`
- [x] Define `JudgeScore` model (per-round scores 0–100 + reasoning string)
- [x] Define `DebateTranscript` model (topic, turns list, scores list, winner)
- [x] Write `tests/test_schemas.py` — valid and invalid cases for all three models

---

## 3. Configuration Module (`config.py`)

- [x] Implement `Settings(BaseSettings)` loading from `.env`
- [x] Define typed fields: `anthropic_api_key`, `model`, `max_rounds`, `min_words`, `max_words`, `rate_limit_rpm`
- [x] Export a module-level `settings = Settings()` singleton
- [x] Verify missing `ANTHROPIC_API_KEY` raises a clear `ValidationError` at startup

---

## 4. Agent Definitions

### 4.1 Base Agent (`agents/base_agent.py`)

- [x] Define `BaseDebateAgent(ABC)` with `name`, `position`, `client` fields
- [x] Declare abstract `argue(round_num, context) -> AgentTurn`
- [x] Implement `_count_words(text: str) -> int`
- [x] Implement `_validate_word_count(text: str) -> bool`
- [x] Implement `_build_system_prompt() -> str` — returns position-anchored prompt
- [x] Implement `_parse_response(raw: str, round_num) -> AgentTurn` with `ValidationError` handling

### 4.2 AI Teacher Agent (`agents/ai_teacher.py`)

- [x] Subclass `BaseDebateAgent` as `AITeacherAgent`
- [x] Set `position` = "AI will completely replace human teachers"
- [x] Define 5 required argument themes in system prompt (personalization, 24/7, analytics, equity, cost)
- [x] Implement `argue(round_num, context) -> AgentTurn`
- [x] Enforce word count `[80–150]`; automatically retry once if out of range

### 4.3 Human Teacher Agent (`agents/human_teacher.py`)

- [x] Subclass `BaseDebateAgent` as `HumanTeacherAgent`
- [x] Set `position` = "Human educators are irreplaceable"
- [x] Define 5 required argument themes (empathy, mentorship, creativity, moral development, safeguarding)
- [x] Implement `argue(round_num, context) -> AgentTurn`
- [x] Enforce word count `[80–150]`; automatically retry once if out of range

---

## 5. Judge Agent (`agents/judge.py`)

- [x] Implement `JudgeAgent` with injected `Anthropic` client and `RateLimiter`
- [x] Implement `next_turn(round_num) -> str` — strict alternating order
- [x] Implement `validate_response(turn: AgentTurn) -> bool` — schema + word count check
- [x] Implement `score_round(ai_turn, human_turn) -> JudgeScore` — 5-criterion rubric (100 pts)
- [x] Implement `declare_winner(transcript: DebateTranscript) -> str` — cumulative totals
- [x] Add tie-breaking logic: if scores equal, winner decided by `reasoning` criterion sum

---

## 6. Gatekeeper / Rate Limiter (`core/gatekeeper.py`)

- [x] Implement `RateLimiter` using token-bucket algorithm
- [x] Initialize bucket capacity and refill rate from `settings.rate_limit_rpm`
- [x] Implement `acquire()` — blocks with `time.sleep` until a token is available
- [x] Implement `tokens_remaining() -> int`
- [x] Log a warning when wait exceeds 5 seconds
- [x] Write `tests/test_gatekeeper.py` — verify blocking and token refill behavior

---

## 7. Debate Engine (`core/debate.py`)

- [x] Implement `DebateEngine` wiring `JudgeAgent`, both debaters, and `RateLimiter`
- [x] Implement `run() -> DebateTranscript` — iterate rounds 1–10 strictly
- [x] Implement `_execute_round(round_num) -> tuple[AgentTurn, AgentTurn]`
- [x] Handle forfeited rounds (invalid response) — log warning, assign score 0
- [x] Implement `_export_transcript(t)` — write `output/transcript.json` after round 10
- [x] Print round-by-round summary to stdout during execution

---

## 8. Utils (`utils/helpers.py`)

- [x] Implement `count_words(text: str) -> int`
- [x] Implement `truncate_context(turns: list, max_turns: int) -> list`
- [x] Implement `format_round_header(round_num: int) -> str`
- [x] Configure module-level `logger = logging.getLogger("ai_debate")`

---

## 9. Main Entry Point (`main.py`)

- [x] Instantiate `Settings`, `Anthropic` client, `RateLimiter`, all agents, `DebateEngine`
- [x] Call `DebateEngine.run()` and print the final verdict to stdout
- [x] Handle `KeyboardInterrupt` — print partial transcript before exit
- [x] Handle `anthropic.APIError` — log message and exit with code 1

---

## 10. Validation, Error Handling & Edge Cases

- [x] Agent returns invalid JSON → forfeit round, score = 0, continue
- [x] Agent exceeds word count after retry → apply –10 pt format penalty
- [x] All 20 pings must fire — no early termination under any condition
- [x] Confirm tie is mathematically impossible given 5-criterion scoring rules

---

## 11. Testing

- [x] `tests/test_schemas.py` — valid/invalid `AgentTurn`, `JudgeScore`, `DebateTranscript`
- [x] `tests/test_agents.py` — mock API, verify retry and word-count enforcement
- [x] `tests/test_gatekeeper.py` — token-bucket blocks and releases correctly
- [x] `tests/test_debate.py` — full 2-round smoke test with mocked agents
- [x] Run `pytest --tb=short` — all tests green
- [x] Run `ruff check src/` and `mypy src/` — zero errors

---

## 12. v1.1 Quality & Display Improvements

- [x] Modify Agent System Prompts — reduce `max_words` to 120, add explicit Judge penalty warning, add density-over-length instruction to `AI_Teacher_Agent` and `Human_Teacher_Agent`
- [x] Refactor Controller Logging — replace `[:100]` truncation in `core/debate.py` with `textwrap.fill()` (width=100) via new `_print_turn()` helper so no argument text is cut off
- [ ] Test Terminal Display — run `uv run debate` from a standalone terminal and confirm all 10 rounds print full wrapped text with no truncation or Unicode errors

---

## 13. v1.2 Active Judge Moderation

- [x] Add `introduce_agent(agent_name, round_num) -> str` to `JudgeAgent` — template intro printed before each agent speaks
- [x] Add `interim_feedback(agent_name, argument) -> str` to `JudgeAgent` — one CLI call after each individual agent argument (replaces end-of-round summary)
- [x] Add `transition_to(from_agent, to_agent, feedback) -> str` to `JudgeAgent` — template transition embedding the interim insight
- [x] Update `_execute_round()` in `debate.py` — print judge intro, argue, print turn, call interim_feedback, print transition for AI; repeat for Human; print judge insight after Human
- [x] Remove "Round Summary" print from `run()` — replaced by two per-agent Judge insights per round
- [x] Update PRD.md — Judge responsibilities, word count table, success criteria
- [x] Update PLAN.md — new section 6 (Active Judge Moderation), updated turn-loop diagram, updated JudgeAgent class signature
- [x] Verify 29 tests pass, ruff clean, mypy clean
- [ ] Test live terminal run — confirm intro/insight/transition lines print correctly for all 10 rounds
