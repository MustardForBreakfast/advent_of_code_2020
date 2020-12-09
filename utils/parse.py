"""Utilities for parsing challenge data."""

import typing as t
from pathlib import Path


def parse_file(relative_path: str) -> str:
    return Path(relative_path).read_text()


def get_lines(data: str) -> t.Tuple[str, ...]:
    """Return the individual lines of a string."""
    return tuple(data.split("\n"))


def parse_to_lines(relative_path: str) -> t.Tuple[str, ...]:
    return get_lines(parse_file(relative_path))
