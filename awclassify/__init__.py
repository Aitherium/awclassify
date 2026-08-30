"""awclassify — Aither World Classify.

Classify any document the way the platform does: WHAT it is (doc_type),
WHO may read it (visibility), WHO it is for (audience), and WHAT it is
about (topics). A standalone, zero-dependency client for a classify-shaped
server, with a deterministic local classifier that works with no network.

Two modes:
  - local rules  — offline, deterministic, from filename/title/source.
                  NEVER asserts "public" without an explicit marker.
  - server       — POST the document to a classify-shaped surface
                  (the AitherOS platform's /classify, or any server
                  speaking the same contract) for the full LLM-powered
                  classification with confidence scores.

Fail-closed contract: a classification you cannot verify is NOT public.
`classified: False` with `visibility: internal` is the honest answer to
"can I ship this" until the server says otherwise.
"""

from awclassify.rules import classify_rules
from awclassify.taxonomy import AUDIENCES, DOC_TYPES, VISIBILITIES

__version__ = "0.1.0"
__all__ = ["classify_rules", "DOC_TYPES", "VISIBILITIES", "AUDIENCES", "__version__"]
