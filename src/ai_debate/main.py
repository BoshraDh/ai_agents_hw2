from __future__ import annotations

import logging
import sys

from .agents.ai_teacher import AITeacherAgent
from .agents.human_teacher import HumanTeacherAgent
from .agents.judge import JudgeAgent
from .config import settings
from .core.cli_client import CLIClient
from .core.debate import DebateEngine
from .core.gatekeeper import RateLimiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main() -> None:
    try:
        client = CLIClient()
        gatekeeper = RateLimiter(rpm=settings.rate_limit_rpm)
        ai_agent = AITeacherAgent(client=client, gatekeeper=gatekeeper)
        human_agent = HumanTeacherAgent(client=client, gatekeeper=gatekeeper)
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
    except RuntimeError as exc:
        logging.error(str(exc))
        sys.exit(1)
    except Exception as exc:
        logging.error(f"Unexpected error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
