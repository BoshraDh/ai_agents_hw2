from __future__ import annotations

import logging
import sys

import anthropic

from .agents.ai_teacher import AITeacherAgent
from .agents.human_teacher import HumanTeacherAgent
from .agents.judge import JudgeAgent
from .config import settings
from .core.debate import DebateEngine
from .core.gatekeeper import RateLimiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main() -> None:
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        gatekeeper = RateLimiter(rpm=settings.rate_limit_rpm)
        ai_agent = AITeacherAgent(client=client)
        human_agent = HumanTeacherAgent(client=client)
        judge = JudgeAgent(client=client, gatekeeper=gatekeeper)
        engine = DebateEngine(
            judge=judge,
            ai_agent=ai_agent,
            human_agent=human_agent,
            gatekeeper=gatekeeper,
        )
        engine.run()
    except KeyboardInterrupt:
        print("\nDebate interrupted by user. Exiting.")
        sys.exit(0)
    except anthropic.APIError as exc:
        logging.error(f"Anthropic API error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
