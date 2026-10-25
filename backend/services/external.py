"""
Example external-API integration with timeouts, retries and graceful failure.

Judges mark "Technical Implementation" partly on how you handle the unhappy path.
Copy this pattern for every third-party call you make.
"""
from __future__ import annotations

import asyncio
import logging
import os

import httpx

log = logging.getLogger("rechersion.external")

EXTERNAL_URL = os.getenv("EXTERNAL_API_URL", "https://httpbin.org/post")
EXTERNAL_KEY = os.getenv("EXTERNAL_API_KEY", "")
TIMEOUT = float(os.getenv("EXTERNAL_TIMEOUT", "8"))
RETRIES = int(os.getenv("EXTERNAL_RETRIES", "2"))


async def call_external_api(text: str) -> dict:
    """
    POSTs to a third-party API with bounded retries and exponential backoff.

    Returns a dict with either 'ok': True + data, or 'ok': False + reason.
    It never raises — a failing third party must not break your demo.
    """
    headers = {"Content-Type": "application/json"}
    if EXTERNAL_KEY:
        headers["Authorization"] = f"Bearer {EXTERNAL_KEY}"

    last_error = "unknown"
    for attempt in range(1, RETRIES + 2):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(EXTERNAL_URL, json={"text": text}, headers=headers)
                resp.raise_for_status()
                return {"ok": True, "status": resp.status_code, "data": resp.json(), "attempt": attempt}

        except httpx.TimeoutException:
            last_error = f"timeout after {TIMEOUT}s"
        except httpx.HTTPStatusError as exc:
            last_error = f"HTTP {exc.response.status_code}"
            if exc.response.status_code < 500:
                break  # client error — retrying won't help
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"

        log.warning("external call failed (attempt %d/%d): %s", attempt, RETRIES + 1, last_error)
        if attempt <= RETRIES:
            await asyncio.sleep(0.5 * (2 ** (attempt - 1)))  # 0.5s, 1.0s, 2.0s

    return {"ok": False, "reason": last_error}
