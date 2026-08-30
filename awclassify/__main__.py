"""python -m awclassify — same as the `awclassify` console script."""

import sys

from awclassify.cli import main

if __name__ == "__main__":
    sys.exit(main())
