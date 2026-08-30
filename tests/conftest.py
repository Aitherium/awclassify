"""Make the package importable from a plain pytest run (no editable install)."""

import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parents[1]  # .../awclassify
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))
