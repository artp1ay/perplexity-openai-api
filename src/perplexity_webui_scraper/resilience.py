"""Resilience utilities for HTTP requests."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import choice
from threading import Lock
from time import monotonic, sleep
from typing import TYPE_CHECKING, TypeVar

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter


if TYPE_CHECKING:
    from collections.abc import Callable

    from tenacity import RetryCallState


T = TypeVar("T")

BROWSER_PROFILES: tuple[str, ...] = (
    "chrome",
    "chrome110",
    "chrome116",
    "chrome119",
    "chrome120",
    "chrome123",
    "chrome124",
    "chrome131",
    "edge99",
    "edge101",
    "safari15_3",
    "safari15_5",
    "safari17_0",
    "safari17_2_ios",
)


@dataclass(slots=True)
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: float = 0.5


@dataclass
class RateLimiter:
    """Token bucket rate limiter."""

    requests_per_second: float = 0.5
    _last_request: float = field(default=0.0, init=False)
    _lock: Lock = field(default_factory=Lock, init=False)

    def acquire(self) -> None:
        """Wait until a request can be made within rate limits."""

        with self._lock:
            now = monotonic()
            min_interval = 1.0 / self.requests_per_second

            if self._last_request > 0:
                elapsed = now - self._last_request
                wait_time = min_interval - elapsed

                if wait_time > 0:
                    sleep(wait_time)

            self._last_request = monotonic()


def get_random_browser_profile() -> str:
    """Get a random browser profile for fingerprint rotation."""

    return choice(BROWSER_PROFILES)


def create_retry_decorator(
    config: RetryConfig,
    retryable_exceptions: tuple[type[Exception], ...],
    on_retry: Callable[[RetryCallState], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Create a tenacity retry decorator with the given configuration."""

    return retry(
        stop=stop_after_attempt(config.max_retries + 1),
        wait=wait_exponential_jitter(
            initial=config.base_delay,
            max=config.max_delay,
            jitter=config.max_delay * config.jitter,
        ),
        retry=retry_if_exception_type(retryable_exceptions),
        before_sleep=on_retry,
        reraise=True,
    )
