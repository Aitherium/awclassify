# awclassify

**Aither World Classify** — classify any document: *what it is*, *who may
read it*, *who it is for*, *what it is about*. A standalone, zero-dependency
CLI + client, public and pip-installable, for the Aither World stack.

```bash
pip install awclassify

awclassify classify report.md
# doc_type    report
# visibility  internal
# audience    other
# topics      -
# engine      rules   classified=False
#
# NOT VERIFIED: rules-only classification. Pass --server for the full
# engine. Per the fail-closed contract, do not publish on this alone.
```

## What it answers

| field | meaning | vocabulary |
|---|---|---|
| `doc_type` | what it is | deck, blog, prd, transcript, report, memo, decision, spec, docs, guide, code, data, email, social, minutes, contract, research, other |
| `visibility` | who may read it | public, internal, confidential |
| `audience` | who it is for | customers, investors, partners, general_public, internal, agents, regulatory, other |
| `topics` | what it is about | 1–5 free-form tags |

## The fail-closed contract

A classification you cannot verify is **NOT public**.

- `classified: False` means the output is heuristic only — do not publish
  the document on it.
- The rules path never asserts `public` from a filename alone; an explicit
  marker (`public/`, `.public.`) is required.
- When the server cannot be reached, the client returns
  `classified: False, visibility: internal` with the reason — never a
  fabricated answer.

To publish a document you need the server-verified answer:

```bash
awclassify classify deck.json --server https://your-platform/doc-classify \
  --token "$PLATFORM_BEARER" --json | jq .visibility
# "public"  ← only now may a stranger read it
```

## Modes

- **Local rules** (default, offline): deterministic classification from the
  filename, title and source type. Zero network, zero dependencies.
- **Server**: `--server URL` posts the document to any classify-shaped
  surface — the AitherOS platform's `/classify`, or anything implementing
  the same contract — for the full LLM-powered classification with
  confidence scores. `--require-server` makes an unreachable surface an
  error instead of a downgrade.

```bash
awclassify taxonomy                      # the fixed vocabulary, offline
awclassify taxonomy --server URL         # ...and diff it against the server's
```

## Why it exists

A $35K revenue figure shipped in a public slide deck because nothing asked
what the document was or who could see it. `awclassify` makes that answer
exist as data before anything ships — one command, no credentials required
for the local tier.

## Relationship to the platform

`awclassify` is the **client brick**. The service half — the engine
(`lib.knowledge.DocClassifier`), the genesis `/doc-classify` router, and the
Nexus-ingest integration — lives in the AitherOS platform as
`aitherclassify`. The taxonomy parity between the two copies is asserted by
the platform's `check_classify_taxonomy_parity` gate.

## Development

```bash
python -m pytest tests/
```
