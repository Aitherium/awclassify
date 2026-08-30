"""The fixed classification vocabulary — standalone copy.

This file is the PUBLIC copy of the taxonomy. The platform engine's copy
lives in `lib.knowledge.DocClassifier`; the parity gate
(`check_classify_taxonomy_parity.py`) asserts the two stay in step, because
two copies of a rule set drift — the same shape as the shared browser
inference worker, and the reason that lesson is a gate here rather than a
comment.
"""

DOC_TYPES = [
    "deck", "blog", "prd", "report", "transcript", "memo", "decision",
    "spec", "docs", "guide", "code", "data", "email", "social", "minutes",
    "contract", "research", "other",
]

VISIBILITIES = ["public", "internal", "confidential"]

AUDIENCES = [
    "customers", "investors", "partners", "general_public", "internal",
    "agents", "regulatory", "other",
]
