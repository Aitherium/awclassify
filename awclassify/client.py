"""Client for a classify-shaped server.

Zero dependencies (stdlib urllib). Speaks the contract of the platform's
`/classify` surface — POST a document, get back the classification — and of
any server that implements the same shape:

    POST /classify
    {"content": "...", "title": "...", "source_type": "..."}
    -> {"classification": {doc_type, visibility, audience, topics, ...}}

Auth is optional: a Bearer token (platform sessions), or an internal key
(sent as X-Internal-Key + X-Caller-Type: platform for self-hosted platform
servers). On ANY failure the client returns the fail-closed shape
(classified=False, visibility="internal") with the reason — it never
fabricates a classification.
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict

DEFAULT_SURFACE = "http://127.0.0.1:8001/doc-classify"
# NOT /classify: on the AitherOS platform that path is the INTENT classifier's
# (first handler wins, measured 2026-08-29) — the document surface is
# /doc-classify. Any classify-shaped server may of course use any path.

FAIL_CLOSED = {
    "classified": False,
    "engine": "none",
    "visibility": "internal",
    "reasons": ["client: surface unreachable"],
}


class ClassifyClient:
    """Minimal client for POST /classify on a classify-shaped server."""

    def __init__(self, surface: str = "", token: str = "",
                 internal_key: str = "", timeout: float = 200.0):
        # 200s default: a classify-shaped server's LLM round trip is minutes,
        # not seconds (measured live 2026-08-29 on the platform: ~2 min).
        self.surface = (surface or DEFAULT_SURFACE).rstrip("/")
        self.token = token
        self.internal_key = internal_key
        self.timeout = timeout

    def classify(
        self,
        content: str,
        *,
        title: str = "",
        source_type: str = "",
        filename: str = "",
    ) -> Dict[str, Any]:
        """Classify a document. Fail-closed shape on ANY failure."""
        payload = json.dumps({
            "content": content,
            "title": title,
            "source_type": source_type,
            "filename": filename,
        }).encode("utf-8")
        req = urllib.request.Request(
            self.surface,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        if self.internal_key:
            req.add_header("X-Internal-Key", self.internal_key)
            req.add_header("X-Caller-Type", "platform")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310 — surface is user-configured
                data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, dict) and isinstance(data.get("classification"), dict):
                return data["classification"]
            if isinstance(data, dict) and "doc_type" in data:
                return data
            return dict(FAIL_CLOSED, reasons=["client: unexpected response shape"])
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
            return dict(FAIL_CLOSED, reasons=[f"client: {type(e).__name__}: {e}"])
