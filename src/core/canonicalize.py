"""Canonicalization and deterministic hashing utilities.

Functions:
- canonicalize_json(dict) -> str: returns a deterministic JSON string for a mapping.
- canonicalize_text(str) -> str: normalize line endings and whitespace.
- compute_checksum(content) -> str: SHA256 hex of bytes or str input.
- compute_deterministic_seed(sources: Dict[str,str], generator_version: Optional[str]=None) -> str:
    produce a deterministic seed based on provided sources (order-independent).
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, Optional


def canonicalize_text(text: str) -> str:
    """Normalize text: normalize line endings to LF and strip trailing/leading whitespace.

    This does not attempt to alter semantic whitespace within lines beyond trimming
    leading/trailing whitespace and normalizing line endings for determinism.
    """
    if text is None:
        return ""
    # Normalize Windows/Mac line endings to LF
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing spaces on each line and overall leading/trailing whitespace
    normalized = "\n".join(line.rstrip() for line in normalized.split("\n"))
    return normalized.strip()


def canonicalize_json(obj: Dict) -> str:
    """Return a canonical JSON string for the given mapping.

    - Sort object keys recursively
    - Use compact separators to avoid insignificant whitespace
    - Ensure non-ASCII characters are preserved (ensure_ascii=False)
    """
    def _prepare(o):
        if isinstance(o, dict):
            return {k: _prepare(o[k]) for k in sorted(o.keys())}
        if isinstance(o, list):
            return [_prepare(i) for i in o]
        return o

    prepared = _prepare(obj)
    return json.dumps(prepared, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_checksum(content: Optional[bytes | str]) -> str:
    """Compute SHA256 hex digest for the provided content.

    Accepts bytes or str. For str input, UTF-8 encoding is used.
    Returns 64-character hex string.
    """
    if content is None:
        content_bytes = b""
    elif isinstance(content, bytes):
        content_bytes = content
    else:
        content_bytes = str(content).encode("utf-8")
    h = hashlib.sha256()
    h.update(content_bytes)
    return h.hexdigest()


def compute_deterministic_seed(sources: Dict[str, str], generator_version: Optional[str] = None) -> str:
    """Compute a deterministic seed from a mapping of source path -> textual content.

    The function normalizes each source's text (via `canonicalize_text`), builds a
    canonical JSON mapping with sorted paths, and returns the SHA256 hex digest of the
    combined representation. If `generator_version` is provided it is prepended to the
    canonicalized payload to bind the seed to a generator version.

    The result is order-independent and stable for identical inputs.
    """
    normalized_sources = {path: canonicalize_text(text) for path, text in sources.items()}
    canonical = canonicalize_json(normalized_sources)
    if generator_version:
        payload = f"{generator_version}:{canonical}"
    else:
        payload = canonical
    return compute_checksum(payload)
