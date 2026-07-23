from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class HttpClient:
    user_agent: str
    timeout_seconds: float = 30.0
    max_retries: int = 4
    sleep_seconds: float = 0.25

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, params=params, headers=headers, timeout=self.timeout_seconds
                )
                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt == self.max_retries - 1:
                    break
                time.sleep(self.sleep_seconds * (2 ** attempt))
        raise RuntimeError(f"GET failed after {self.max_retries} attempts: {url}") from last_error

    def get_text(self, url: str) -> tuple[str, str]:
        headers = {"User-Agent": self.user_agent, "Accept": "text/html"}
        response = requests.get(url, headers=headers, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.text, response.headers.get("content-type", "")
