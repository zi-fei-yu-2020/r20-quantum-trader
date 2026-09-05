"""Bounded retries for inference only. Never use this transport for orders.

Retries preserve every payload field, including model, high reasoning effort and
JSON mode. Errors deliberately exclude prompts, credentials and upstream bodies.
"""
from __future__ import annotations
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import errno
import json
import logging
import math
import socket
import ssl
import time
import urllib.error
import urllib.request
from typing import Any

LOG = logging.getLogger(__name__)
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class LLMRequestError(RuntimeError):
    def __init__(self, status_code: int, attempts: int, category: str):
        self.status_code = status_code
        self.attempts = attempts
        self.category = category
        label = f"HTTP {status_code}" if status_code else category
        super().__init__(f"模型请求失败：{label}，已尝试 {attempts} 次；未更换模型或降低思考强度")


def retry_delay(header: str | None, attempt: int) -> float:
    if header:
        try:
            seconds = float(header)
        except ValueError:
            try:
                date = parsedate_to_datetime(header)
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
                seconds = (date - datetime.now(timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                seconds = -1
        if math.isfinite(seconds) and seconds >= 0:
            return seconds
    return 0.5 * (2 ** (attempt - 1))


def _transient_network_error(error: BaseException) -> bool:
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    if isinstance(reason, ssl.SSLError):
        return False  # Never retry around certificate validation failures.
    return isinstance(reason, (TimeoutError, ConnectionError)) or (
        isinstance(reason, OSError)
        and reason.errno in {errno.ECONNRESET, errno.ECONNREFUSED, errno.ETIMEDOUT, socket.EAI_AGAIN}
    )


def request_json(endpoint: str, headers: dict[str, str], payload: dict[str, Any], timeout: float,
                 max_attempts: int = 3) -> tuple[dict[str, Any], int, int, int]:
    """Return JSON, HTTP status, end-to-end latency and attempts used.

    All attempts share one timeout budget. Retry-After is respected: when it
    exceeds the remaining budget, fail instead of sending an early retry.
    """
    if not math.isfinite(timeout) or timeout <= 0 or not 1 <= max_attempts <= 3:
        raise ValueError("Invalid inference timeout or retry limit")
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    start = time.monotonic()
    deadline = start + timeout
    for attempt in range(1, max_attempts + 1):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise LLMRequestError(0, attempt - 1, "deadline_exceeded")
        status = 0
        delay_header = None
        category = "network_error"
        retryable = False
        failure: BaseException | None = None
        try:
            request = urllib.request.Request(endpoint, data=encoded, headers=headers)
            with urllib.request.urlopen(request, timeout=remaining) as response:
                status = response.getcode()
                decoded = json.loads(response.read().decode("utf-8"))
            if not isinstance(decoded, dict) or decoded.get("error"):
                raise LLMRequestError(status, attempt, "invalid_response")
            return decoded, status, round((time.monotonic() - start) * 1000), attempt
        except urllib.error.HTTPError as exc:
            status = exc.code
            category = "http_error"
            delay_header = exc.headers.get("Retry-After") if exc.headers else None
            retryable = status in RETRYABLE_STATUS
            failure = exc
            exc.close()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            retryable = _transient_network_error(exc)
            failure = exc
        except (ValueError, UnicodeError) as exc:
            raise LLMRequestError(status, attempt, "invalid_json_response") from exc
        delay = retry_delay(delay_header, attempt)
        if not retryable or attempt == max_attempts or delay >= deadline - time.monotonic():
            raise LLMRequestError(status, attempt, category) from failure
        LOG.warning("LLM transient failure status=%s; retry=%s/%s delay=%.2fs",
                    status or category, attempt + 1, max_attempts, delay)
        time.sleep(delay)
    raise AssertionError("Unreachable")
