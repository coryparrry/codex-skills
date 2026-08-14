#!/usr/bin/env python3
"""Check an App Review Notes draft against a UTF-8 byte limit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEFAULT_LIMIT = 4_000


def evaluate(text: str, limit: int = DEFAULT_LIMIT) -> dict[str, int | bool]:
    """Return the UTF-8 byte count and limit result without exposing the text."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    used = len(text.encode("utf-8"))
    return {
        "bytes": used,
        "limit": limit,
        "remaining": limit - used,
        "within_limit": used <= limit,
    }


def read_text(path: str) -> str:
    """Read UTF-8 text from a path or stdin when path is '-'."""
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count UTF-8 bytes in App Review Notes without printing the notes."
    )
    parser.add_argument("path", help="UTF-8 text file, or '-' to read stdin")
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"byte limit to enforce (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable result",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = evaluate(read_text(args.path), args.max_bytes)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        state = "within limit" if result["within_limit"] else "over limit"
        print(
            f"Review Notes: {result['bytes']}/{result['limit']} UTF-8 bytes "
            f"({result['remaining']:+d} remaining, {state})"
        )

    return 0 if result["within_limit"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
