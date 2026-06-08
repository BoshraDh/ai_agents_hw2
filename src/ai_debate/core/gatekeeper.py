from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger("ai_debate")


class RateLimiter:
    """Token-bucket rate limiter — one token consumed per API call."""

    def __init__(self, rpm: int = 10) -> None:
        self._rpm = rpm
        self._tokens: float = float(rpm)
        self._lock = threading.Lock()
        self._last_refill = time.monotonic()

    @property
    def _refill_rate(self) -> float:
        return self._rpm / 60.0  # tokens per second

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(float(self._rpm), self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    def acquire(self) -> None:
        """Block until a token is available, then consume it."""
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._refill_rate

            if wait > 5.0:
                logger.warning(f"Rate limit reached — waiting {wait:.1f}s before next API call")
            time.sleep(wait)

    def release(self) -> None:
        with self._lock:
            self._tokens = min(float(self._rpm), self._tokens + 1.0)

    def tokens_remaining(self) -> int:
        with self._lock:
            self._refill()
            return int(self._tokens)
