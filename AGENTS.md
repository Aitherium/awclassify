# awclassify for agents

Read this if you are an agent (or a human) editing this package. Short on
purpose: the commands, the traps that cost a session, and where the rest lives.
Nothing here is read at runtime — it is for you.

## What this is

PyPI distribution **`awclassify`** (version in `pyproject.toml`), import
package `awclassify`, Python >= 3.10. Classify any document — what it is, who
may read it, who it is for, what it is about.

This repository is a **synced mirror** of the AitherOS monorepo (lane
`.github/workflows/sync-awclassify.yml`). Hand edits made here are overwritten
on the next sync — change the source and let the lane publish.

## Build, test, verify

```bash
python -m pytest tests -q        # the suite: 13 tests, green at v0.1.0
pip install -e .                 # editable install for developing against it
```

The suite was run from a source checkout with no prior install. The publish
lane (`publish-brick.yml`) additionally builds the wheel, installs it and
imports it — a tree that tests green can still ship a broken wheel.

## Rules that keep this useful

- **Standalone is a tested mode, not an aspiration.** `test_standalone.py`
  pins the brick working with no platform behind it — a classification that
  only works when a fleet answers is not a brick.
- **The four questions stay four answers.** Who-may-read is a sensitivity
  judgment: never fold it into a topic label, or a document's audience
  silently becomes whatever the classifier found most interesting about it.
- **The registry drives the public surface.** This repo's README header,
  `llms.txt` and `aither-manifest.json` are generated from the ecosystem
  registry (one yaml in the AitherOS monorepo) and rewritten on every sync.
  Change the registry; do not hand-edit the generated blocks.

## Read next

- `llms.txt` — the install/use card written for an agent to execute
- `README.md` — the human front door
- `docs/` — the generated docs site source
