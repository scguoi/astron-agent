from __future__ import annotations

from typing import Any

import requests

from workflow_trace.configs import settings


class SearchManager:
    def __init__(self) -> None:
        self.base_url = settings.es_url.rstrip("/")
        self.timeout = settings.es_timeout_seconds
        self.verify = settings.es_verify
        self.auth = None
        if settings.es_username:
            self.auth = (settings.es_username, settings.es_password)

    def search(self, index: str, body: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/{index}/_search",
            json=body,
            timeout=self.timeout,
            verify=self.verify,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()
