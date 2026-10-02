"""OFFLINE ISBN lookup stub.

ISBN metadata is resolved from a bundled JSON catalog
(`isbn_catalog.json`) that ships with the app. This module makes
**no network calls** — unknown ISBNs simply return None, and the UI
falls back to manual entry.
"""
import json
from functools import lru_cache
from pathlib import Path

_CATALOG_PATH = Path(__file__).with_name("isbn_catalog.json")


@lru_cache(maxsize=1)
def _catalog() -> dict:
    entries = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    return {normalize_isbn(e["isbn"]): e for e in entries}


def normalize_isbn(raw: str | None) -> str:
    """Strip dashes/spaces; keep digits (and a trailing X for ISBN-10)."""
    if not raw:
        return ""
    return "".join(ch for ch in raw if ch.isdigit() or ch.lower() == "x").upper()


def lookup_isbn(raw: str | None) -> dict | None:
    """Return {'isbn','title','author','pages'} for a known ISBN, else None."""
    return _catalog().get(normalize_isbn(raw))


def catalog_size() -> int:
    return len(_catalog())
