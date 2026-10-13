"""Entry point: ``python -m forge_host`` or the ``forge`` console script."""

from __future__ import annotations

import sys

from forge_host.bootstrap.app import run


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())