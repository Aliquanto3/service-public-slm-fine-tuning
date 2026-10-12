"""Permet `python -m slmsp` (préférer `uv run slmsp`)."""

from slmsp.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
