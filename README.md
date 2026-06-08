# AI vs. Human Teachers — 3-Agent Debate System

An automated debate system using three autonomous AI agents to argue the topic:

> **"Will AI completely replace human teachers within a few years to deliver more effective education, or is the human element irreplaceable?"**

---

## Agents

| Agent | Role | Position |
|-------|------|----------|
| `AI_Teacher_Agent` | Debater | AI will fully replace human teachers |
| `Human_Teacher_Agent` | Debater | Human educators are irreplaceable |
| `JudgeAgent` | Moderator & Arbiter | Introduces, scores, and declares winner |

### Judge Flow (per round)
```
[Judge] Round N -- AI Teacher, please present your argument.
  AI   : <argument>
  [Judge] <one-sentence insight> -- Now, Human Teacher, your response.
  Human: <argument>
  [Judge] <one-sentence insight>
  [Scores] AI: NN | Human: NN
```

---

## Project Structure

```
ai_agents_hw2/
├── src/
│   └── ai_debate/
│       ├── main.py                # Entry point
│       ├── config.py              # Settings (pydantic-settings + .env)
│       ├── agents/
│       │   ├── base_agent.py      # Abstract base class
│       │   ├── ai_teacher.py      # Pro-AI debater
│       │   ├── human_teacher.py   # Pro-human debater
│       │   └── judge.py           # Moderator, scorer, and arbiter
│       ├── core/
│       │   ├── debate.py          # Turn-loop engine
│       │   ├── cli_client.py      # Subprocess wrapper for claude CLI
│       │   └── gatekeeper.py      # Token-bucket rate limiter
│       ├── models/
│       │   └── schemas.py         # Pydantic v2 schemas
│       └── utils/
│           └── helpers.py         # Word count, context truncation
├── tests/                         # 29 pytest tests
├── docs/
│   ├── PRD.md                     # Product Requirements Document
│   ├── PLAN.md                    # Technical Architecture
│   └── TODO.md                    # Implementation Checklist
├── logs/                          # Per-round JSON logs (auto-created)
├── output/                        # Final transcript (auto-created)
├── pyproject.toml
└── .env.example
```

---

## Requirements

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) package manager
- [Claude Code CLI](https://claude.ai/code) — authenticated and available as `claude` in PATH

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/BoshraDh/ai_agents_hw2.git
cd ai_agents_hw2

# 2. Install dependencies
uv sync

# 3. Copy env file (no API key needed -- uses claude CLI)
cp .env.example .env
```

---

## Running the Debate

Open a **standalone terminal** (not inside Claude Code) and run:

```bash
uv run debate
```

The debate runs 10 rounds (20 total agent turns). Output is printed live to the terminal and saved to:
- `logs/debate_transcript.json` — per-round log updated in real time
- `output/transcript.json` — full transcript exported after round 10

---

## Debate Rules

| Parameter | Value |
|-----------|-------|
| Rounds | 10 per agent (20 total exchanges) |
| Turn order | AI Teacher -> Human Teacher (strict alternation) |
| Argument length | 80-120 words (penalty for exceeding) |
| Scoring | 5 criteria, 100 pts per agent per round |
| Winner | Cumulative score -- no ties permitted |

### Scoring Criteria

| Criterion | Points |
|-----------|--------|
| Logical reasoning depth | 30 |
| Evidence quality | 25 |
| Relevance to topic | 20 |
| Format / schema compliance | 15 |
| Word count adherence | 10 |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12+ |
| Package manager | `uv` |
| Schema validation | Pydantic v2 |
| Config | pydantic-settings + `.env` |
| LLM backend | Claude CLI subprocess (`claude -p`) |
| Rate limiting | Token-bucket (`RateLimiter`) |
| Linting | ruff |
| Type checking | mypy |
| Testing | pytest (29 tests) |

---

## Development

```bash
# Run tests
uv run pytest --tb=short

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

---

## Output Example

```
============================================================
DEBATE TOPIC:
AI vs. Human Teachers: Will AI completely replace human teachers...
============================================================
--- Round 1 ---
  [Judge] Round 1 -- AI Teacher, please present your argument.
  AI   : AI-powered adaptive learning platforms already outperform
         traditional classrooms in measurable outcomes...
  [Judge] Strong data-driven opening focused on measurable outcomes. -- Now, Human Teacher, your response.
  Human: Numbers miss what matters most. A teacher who notices a
         student's quiet withdrawal and responds with empathy...
  [Judge] Compelling emotional intelligence argument highlighting irreplaceable human perception.
  [Scores] AI:  74 | Human:  71
...
============================================================
FINAL VERDICT
============================================================
```

---

## Version History

| Version | Description |
|---------|-------------|
| v1.0 | Initial 3-agent debate system |
| v1.1 | Word limit tightened to 120, penalty warning, textwrap display |
| v1.2 | Active Judge moderation -- per-agent intro, insight, and transition |
