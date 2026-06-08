import threading
import time

from ai_debate.core.gatekeeper import RateLimiter


def test_acquire_reduces_tokens():
    rl = RateLimiter(rpm=60)
    before = rl.tokens_remaining()
    rl.acquire()
    assert rl.tokens_remaining() == before - 1


def test_release_restores_token():
    rl = RateLimiter(rpm=60)
    rl.acquire()
    before = rl.tokens_remaining()
    rl.release()
    assert rl.tokens_remaining() >= before


def test_tokens_capped_at_rpm():
    rl = RateLimiter(rpm=10)
    rl.release()
    rl.release()
    assert rl.tokens_remaining() <= 10


def test_tokens_refill_over_time():
    rl = RateLimiter(rpm=60)  # 1 token/second
    for _ in range(rl._rpm):
        rl._tokens = 0.0  # drain manually (no blocking)
    assert rl.tokens_remaining() == 0
    time.sleep(1.1)
    assert rl.tokens_remaining() >= 1


def test_thread_safety():
    rl = RateLimiter(rpm=600)  # high RPM so threads don't block long
    results: list[int] = []

    def task() -> None:
        rl.acquire()
        results.append(1)

    threads = [threading.Thread(target=task) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(results) == 10


def test_initial_tokens_equal_rpm():
    rl = RateLimiter(rpm=15)
    assert rl.tokens_remaining() == 15
