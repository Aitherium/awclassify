"""awclassify CLI.

    awclassify classify <file> [--server URL] [--token T] [--json]
    awclassify taxonomy [--server URL] [--json]

`classify` always runs the deterministic local rules first (offline, never
raises). With `--server` the document is also posted to a classify-shaped
surface for the full LLM-powered classification — and the server's answer
is the one printed when it arrives. Without a server (or when the server is
unreachable) the rules classification is printed with an explicit "not
verified" warning: rules never assert "public", and `classified: False`
means you must not ship the document as public on this output alone.

Exit codes: 0 a classification was produced; 1 the file could not be read
or `--require-server` was given and the surface was unreachable.
"""

import argparse
import json
import sys
from pathlib import Path

from awclassify import __version__
from awclassify.client import ClassifyClient
from awclassify.rules import classify_rules
from awclassify.taxonomy import AUDIENCES, DOC_TYPES, VISIBILITIES

MAX_READ_CHARS = 500_000


def _read_document(path: str) -> str:
    data = Path(path).read_bytes()
    # Decode as UTF-8 with a tolerant fallback (decks and reports are usually
    # UTF-8; a binary file produces a rules-only result with a clear reason).
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
    return text[:MAX_READ_CHARS]


def _print_human(result: dict, warned: bool) -> None:
    print(f"doc_type    {result.get('doc_type', 'other')}")
    print(f"visibility  {result.get('visibility', 'internal')}")
    print(f"audience    {result.get('audience', 'other')}")
    print(f"topics      {', '.join(result.get('topics') or []) or '-'}")
    print(f"engine      {result.get('engine', 'none')}   "
          f"classified={result.get('classified', False)}")
    if result.get("reasons"):
        print("reasons")
        for r in result["reasons"]:
            print(f"  - {r}")
    if warned:
        print("\nNOT VERIFIED: rules-only classification. Pass --server for the full")
        print("engine. Per the fail-closed contract, do not publish on this alone.")


def cmd_classify(args) -> int:
    try:
        content = _read_document(args.file)
    except OSError as e:
        print(f"awclassify: cannot read {args.file}: {e}", file=sys.stderr)
        return 1

    result = classify_rules(content, filename=Path(args.file).name)
    warned = False

    if args.server:
        client = ClassifyClient(surface=args.server, token=args.token,
                                internal_key=args.internal_key)
        server = client.classify(content, title=args.title,
                                 source_type=args.source_type)
        if server.get("classified"):
            result = server  # the server's verified answer wins
        else:
            warned = True
            result = server if server.get("engine") != "none" else result
            if args.require_server:
                for r in server.get("reasons", []):
                    print(f"awclassify: server: {r}", file=sys.stderr)
                return 1
    else:
        warned = True  # rules-only is always "not verified"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result, warned)
    return 0


def cmd_taxonomy(args) -> int:
    local = {"doc_types": DOC_TYPES, "visibilities": VISIBILITIES,
             "audiences": AUDIENCES}
    if args.server:
        # Fetch the server's taxonomy (public endpoint) and report drift.
        import urllib.error
        import urllib.request
        try:
            req = urllib.request.Request(args.server.rstrip("/") + "/taxonomy")  # noqa: S310 — user-configured
            with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
                server = json.loads(resp.read().decode("utf-8"))
            for key in local:
                if local[key] != server.get(key, []):
                    print(f"warning: {key} differs from the server", file=sys.stderr)
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
            print(f"awclassify: cannot fetch server taxonomy: {e}", file=sys.stderr)
    if args.json:
        print(json.dumps(local, indent=2))
    else:
        for key in local:
            print(f"{key}: {', '.join(local[key])}")
    return 0


def main(argv=None) -> int:
    # GENERATED doctor intercept (gen_aw_doctor.py) -- do not edit
    _dv = locals().get("argv")
    if (_dv if _dv is not None else __import__("sys").argv[1:])[:1] == ["doctor"]:
        from ._doctor import report
        return report()
    # GENERATED repo-state intercept (gen_aw_doctor.py) -- do not edit
    try:
        from awgit import state as _aw_state
    except Exception:
        _aw_state = None
    if _aw_state is not None:
        _sv = locals().get("argv")
        if _aw_state.cli_banner(_sv if _sv is not None else __import__("sys").argv[1:]):
            return 0
    parser = argparse.ArgumentParser(
        prog="awclassify",
        description="Classify a document: type, visibility, audience, topics.",
    )
    parser.add_argument("--version", action="version", version=f"awclassify {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("classify", help="classify a document")
    c.add_argument("file")
    c.add_argument("--server", default="", help="classify-shaped server URL")
    c.add_argument("--token", default="", help="Bearer token for the server")
    c.add_argument("--internal-key", default="", dest="internal_key",
                   help="X-Internal-Key for a self-hosted platform server")
    c.add_argument("--title", default="")
    c.add_argument("--source-type", default="", dest="source_type")
    c.add_argument("--require-server", action="store_true",
                   help="exit 1 when the server is unreachable")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_classify)

    t = sub.add_parser("taxonomy", help="print the fixed vocabulary")
    t.add_argument("--server", default="")
    t.add_argument("--json", action="store_true")
    t.set_defaults(func=cmd_taxonomy)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
