# Changelog

## 0.1.0 (2026-08-29)

- First public release. Standalone zero-dependency CLI + client.
- `awclassify classify <file>` — local deterministic rules (offline) with
  optional `--server` upgrade to a classify-shaped surface.
- `awclassify taxonomy` — the fixed vocabulary, with server drift diff.
- Fail-closed contract: rules never assert "public"; an unreachable server
  degrades to `classified: False, visibility: internal` with a reason.
