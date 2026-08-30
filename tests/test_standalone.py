"""Standalone awclassify tests — no network, no server, no monorepo imports.

The rules contract (the fail-closed half) and the CLI plumbing are pinned
here so the public brick cannot regress without a failing test.
"""

import json
from unittest import mock

from awclassify import classify_rules
from awclassify.client import ClassifyClient
from awclassify.taxonomy import AUDIENCES, DOC_TYPES, VISIBILITIES

# ---------------------------------------------------------------------------
# BOUNDARY — the brick must be standalone
# ---------------------------------------------------------------------------

def test_no_monorepo_imports():
    from pathlib import Path

    import awclassify.client
    import awclassify.rules
    pkg = Path(awclassify.rules.__file__).resolve().parent  # the awclassify/ dir
    for py in pkg.glob("*.py"):  # the SHIPPED modules — tests excluded by design
        src = py.read_text(encoding="utf-8")
        for name in ("from lib", "import lib", "from services", "AitherOS/"):
            assert name not in src, f"{py.name} must not reference {name!r}"


def test_taxonomy_is_wellformed():
    assert len(DOC_TYPES) >= 10
    assert "deck" in DOC_TYPES and "other" in DOC_TYPES
    assert VISIBILITIES == ["public", "internal", "confidential"]
    assert "investors" in AUDIENCES
    assert len(set(DOC_TYPES)) == len(DOC_TYPES)


# ---------------------------------------------------------------------------
# RULES CONTRACT
# ---------------------------------------------------------------------------

def test_rules_never_public_from_filename_alone():
    r = classify_rules("", filename="investor-pitch-traction-revenue.deck.json")
    assert r["doc_type"] == "deck"
    assert r["visibility"] == "internal"
    assert r["classified"] is False
    assert r["engine"] == "rules"


def test_rules_explicit_public_marker_is_the_only_public_path():
    assert classify_rules("", filename="docs/public/guide.md")["visibility"] == "public"
    assert classify_rules("", filename="docs/public-guide.md")["visibility"] == "internal"
    assert classify_rules("", filename="public-deck-notes.md")["visibility"] == "internal"


def test_rules_detects_types():
    assert classify_rules("", filename="blog/launch.md")["doc_type"] == "blog"
    assert classify_rules("", filename="session-transcript.txt")["doc_type"] == "transcript"
    assert classify_rules("", filename="PRD-thing.md")["doc_type"] == "prd"
    assert classify_rules("", filename="train.py")["doc_type"] == "code"
    assert classify_rules("", filename="export.csv")["doc_type"] == "data"


def test_rules_result_shape_matches_server_contract():
    r = classify_rules("")
    for key in ("doc_type", "visibility", "audience", "topics",
                "confidence", "engine", "classified", "reasons"):
        assert key in r
    assert isinstance(r["reasons"], list) and r["reasons"]


# ---------------------------------------------------------------------------
# CLIENT FAIL-CLOSED
# ---------------------------------------------------------------------------

def test_client_fails_closed_on_unreachable_surface():
    out = ClassifyClient(surface="http://127.0.0.1:1/classify").classify("x")
    assert out["classified"] is False
    assert out["visibility"] == "internal"
    assert out["engine"] == "none"
    assert any("client" in r for r in out["reasons"])


def test_client_parses_classification_shape():
    def _fake_urlopen(req, timeout=None):
        class _R:
            def read(self):
                return json.dumps({"classification": {
                    "doc_type": "deck", "visibility": "internal",
                    "audience": "investors", "topics": ["revenue"],
                    "engine": "llm", "classified": True,
                }}).encode()
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
        return _R()

    with mock.patch("urllib.request.urlopen", _fake_urlopen):
        out = ClassifyClient(surface="http://x/classify").classify("deck")
    assert out["classified"] is True
    assert out["doc_type"] == "deck"
    assert out["visibility"] == "internal"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_cli_classify_rules_only(tmp_path):
    from awclassify.cli import main
    f = tmp_path / "x.deck.json"
    f.write_text("deck about revenue", encoding="utf-8")
    rc = main(["classify", str(f)])
    assert rc == 0


def test_cli_classify_json(tmp_path):
    from awclassify.cli import main
    f = tmp_path / "x.deck.json"
    f.write_text("deck", encoding="utf-8")
    rc = main(["classify", str(f), "--json"])
    assert rc == 0


def test_cli_require_server_unreachable_exits_1(tmp_path):
    from awclassify.cli import main
    f = tmp_path / "x.deck.json"
    f.write_text("deck", encoding="utf-8")
    rc = main(["classify", str(f), "--server", "http://127.0.0.1:1/classify",
               "--require-server"])
    assert rc == 1


def test_cli_missing_file_exits_1(tmp_path):
    from awclassify.cli import main
    rc = main(["classify", str(tmp_path / "nope.md")])
    assert rc == 1


def test_cli_taxonomy():
    from awclassify.cli import main
    assert main(["taxonomy"]) == 0
