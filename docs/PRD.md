# Product Requirements Document
# AI vs. Human Teachers — 3-Agent Debate System

**Version:** 1.0.0  
**Date:** 2026-06-07  
**Author:** AI Debate System Team  
**Status:** Draft

---

## 1. Overview

This document defines requirements for a structured, automated AI debate system
involving three autonomous agents. The system models a formal academic debate on
the topic:

> **"AI vs. Human Teachers: Will AI completely replace human teachers within a
> few years to deliver more effective education, or is the human element
> irreplaceable?"**

---

## 2. Debate Topic

| Dimension        | Detail                                                          |
|------------------|-----------------------------------------------------------------|
| **Topic**        | AI vs. Human Teachers in Education                             |
| **Pro-AI Side**  | AI will fully replace teachers via hyper-personalization        |
| **Pro-Human Side** | Human educators are irreplaceable — empathy, mentorship, soul |
| **Format**       | Structured alternating rounds, JSON-only communication          |
| **Arbiter**      | Judge Agent (The Father) — objective, reasoning-driven          |

---

## 3. Agents

### 3.1 Judge Agent — "The Father"

- **Role:** Orchestrator and final arbiter
- **Responsibilities:**
  - Controls turn order and enforces strict round limits
  - Validates every response for JSON schema compliance
  - Scores each argument on: reasoning depth, evidence quality, format adherence
  - Declares a single winner at the end — no ties permitted
- **Decision Basis:** Cumulative score across all 10 rounds per agent
- **Behavior:** Objective, neutral, structured; never intervenes in content

### 3.2 AI_Teacher_Agent

- **Side:** Pro-AI replacement
- **Position:** AI will completely replace human teachers within a few years
- **Key Arguments Must Cover:**
  - Hyper-personalized adaptive learning paths
  - 24/7 availability and unlimited scalability
  - Consistent, bias-free delivery of curriculum
  - Real-time performance analytics and gap detection
  - Cost reduction and global education access equity

### 3.3 Human_Teacher_Agent

- **Side:** Pro-human irreplaceability
- **Position:** Human educators cannot be replaced by AI systems
- **Key Arguments Must Cover:**
  - Emotional intelligence and empathetic mentorship
  - Social and moral development beyond curriculum
  - Spontaneous creativity and contextual adaptability
  - Role modeling, inspiration, and intrinsic motivation
  - Ethical oversight and safeguarding responsibilities

---

## 4. Debate Rules

### 4.1 Round Structure

| Parameter              | Value                      |
|------------------------|----------------------------|
| Rounds per agent       | 10                         |
| Total exchanges (pings)| 20                         |
| Turn order             | AI_Teacher → Human_Teacher (alternating) |
| Turn control           | Exclusively managed by Judge |
| Skipping               | Not permitted               |
| Concession             | Not permitted               |

### 4.2 Word Count Limits

| Agent / Message Type   | Min Words | Max Words |
|------------------------|-----------|-----------|
| AI_Teacher_Agent argument  | 80    | 150       |
| Human_Teacher_Agent argument | 80  | 150       |
| Judge round summary    | 30        | 60        |
| Judge final verdict    | 100       | 200       |

Responses outside these bounds are flagged and penalized in scoring.

### 4.3 JSON Communication Protocol

Every agent response **must** conform to the following schema:

```json
{
  "agent": "AI_Teacher_Agent | Human_Teacher_Agent | Judge",
  "round": 1,
  "role": "debater | judge",
  "argument": "string (debater only)",
  "score_awarded": null,
  "round_summary": "string (judge only, per round)",
  "final_verdict": null,
  "word_count": 0,
  "format_valid": true
}
```

Non-conforming responses are rejected and the round is forfeited.

---

## 5. Scoring System

The Judge scores each round immediately after both agents respond.

| Criterion              | Max Points |
|------------------------|-----------|
| Logical reasoning depth | 30        |
| Evidence quality        | 25        |
| Relevance to topic      | 20        |
| Format / schema compliance | 15     |
| Word count adherence    | 10        |
| **Total per round**     | **100**   |

Cumulative scores across 10 rounds determine the winner.  
The Judge must produce a non-tie verdict using these totals.

---

## 6. Final Verdict Requirements

- Issued by the Judge after round 10 of both agents
- Must explicitly name the winner
- Must cite the cumulative score differential
- Must reference at least two deciding arguments by round number
- No tie outcome is permitted under any scoring combination

---

## 7. Technical Requirements

| Requirement         | Specification                                  |
|---------------------|------------------------------------------------|
| Language            | Python 3.12+                                   |
| Package manager     | `uv`                                           |
| Project layout      | `src/` layout with `pyproject.toml`            |
| LLM Backend         | Anthropic Claude API (claude-sonnet-4-6)       |
| Schema validation   | `pydantic` v2                                  |
| Linting             | `ruff`                                         |
| Type checking       | `mypy`                                         |
| Testing             | `pytest`                                       |
| Config              | `pydantic-settings` + `.env`                   |

---

## 8. Out of Scope

- Real-time web UI (CLI output only for v1)
- Multi-language support
- Persistent storage / database
- Human-in-the-loop intervention during debate

---

## 9. Success Criteria

- All 20 rounds complete without schema errors
- Judge produces a valid, reasoned, non-tie verdict
- Word counts enforced on every response
- Full debate transcript exported as structured JSON
