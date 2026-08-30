"""Deterministic local classifier — the offline tier of awclassify.

A standalone twin of the platform engine's rules path
(`lib.knowledge.DocClassifier.rules_classify`), deliberately without any
monorepo import so this package ships to strangers. The parity gate keeps
the taxonomy in step; the rules here are the same shape and intent.

CONTRACT:
  - `classified` is always False in the rules result: rules are heuristics,
    not verification — a stranger must not ship on them.
  - visibility NEVER becomes "public" from a filename alone. An explicit
    PUBLIC marker is required.
  - every decision is recorded in `reasons`.
"""

import re
from typing import Dict, List

#: Explicit markers that let the rules path assert "public" — the ONLY
#: filename/source evidence this module trusts for publicity.
PUBLIC_MARKERS = (".public.", "public/", "PUBLIC.md", "-public")

_TYPE_RULES = [
    (re.compile(r"\.deck\.json$|_deck\.py$|\.pptx?$|slides", re.I), "deck"),
    (re.compile(r"transcript|session-log|conversation-log|chat-log", re.I), "transcript"),
    (re.compile(r"\bprd\b|\.prd|product-requirements|requirements\.md", re.I), "prd"),
    (re.compile(r"decision|adr-|ADR_", re.I), "decision"),
    (re.compile(r"^blog|/blog|posts?/", re.I), "blog"),
    (re.compile(r"minutes|meeting-notes|notes\.md", re.I), "minutes"),
    (re.compile(r"^docs?/|documentation|manual|guide", re.I), "docs"),
    (re.compile(r"contract|agreement|terms|license", re.I), "contract"),
    (re.compile(r"\.(py|ts|tsx|js|go|rs|java|c|cpp|sh)$", re.I), "code"),
    (re.compile(r"\.(csv|json|yaml|yml|xml|parquet|sql)$", re.I), "data"),
    (re.compile(r"research|experiment|benchmark|evaluation", re.I), "research"),
    (re.compile(r"report|summary|status", re.I), "report"),
    (re.compile(r"spec|api[-_.]?doc|design[-_.]?doc", re.I), "spec"),
    (re.compile(r"memo|brief", re.I), "memo"),
]

_AUDIENCE_RULES = [
    (re.compile(r"^customers?/|customer-facing|sales", re.I), "customers"),
    (re.compile(r"investor|pitch|fundraising|cap-table", re.I), "investors"),
    (re.compile(r"partner|integrat", re.I), "partners"),
    (re.compile(r"regulatory|compliance|audit", re.I), "regulatory"),
    (re.compile(r"^internal|internal-", re.I), "internal"),
]


def classify_rules(
    content: str = "",
    *,
    filename: str = "",
    title: str = "",
    source_type: str = "",
) -> Dict:
    """Deterministic classification from filenames, titles and source types.

    Zero I/O, zero network, zero dependencies. Never raises. Always returns
    the full result shape with `classified: False` and `reasons` — the same
    shape a classify-shaped server returns, so consumers handle one contract.
    """
    haystack = " ".join(filter(None, [filename, title, source_type]))
    reasons: List[str] = []

    doc_type = "other"
    for pat, t in _TYPE_RULES:
        if pat.search(haystack):
            doc_type = t
            reasons.append(f"rules: type={t} (matched {pat.pattern})")
            break

    audience = "other"
    for pat, a in _AUDIENCE_RULES:
        if pat.search(haystack):
            audience = a
            reasons.append(f"rules: audience={a}")
            break

    topics: List[str] = []
    if any(k in haystack.lower() for k in ("revenue", "sales", "deal", "customer")):
        topics.append("business")
    if any(k in haystack.lower() for k in ("agent", "ai", "llm", "model")):
        topics.append("ai")

    visibility = "internal"
    if any(m in haystack for m in PUBLIC_MARKERS):
        visibility = "public"
        reasons.append("rules: visibility=public (explicit PUBLIC marker)")

    return {
        "doc_type": doc_type,
        "visibility": visibility,
        "audience": audience,
        "topics": topics,
        "confidence": 0.55 if reasons else 0.0,
        "engine": "rules",
        "classified": False,
        "reasons": reasons or ["rules: no evidence matched"],
    }
