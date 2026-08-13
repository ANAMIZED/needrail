"""Content-addressed storage helpers for multi-node NeedRail.

Phase-1 uses local JSON. This module provides the hashing and
canonicalization primitives so any node can later share the same
content-addressed objects without a central database.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(obj: Any, algorithm: str = "sha256") -> str:
    """
    Compute a content hash for any NeedRail object.
    Returns "sha256:<hex>" so nodes can verify integrity.
    """
    data = canonical_json(obj).encode("utf-8")
    h = hashlib.new(algorithm, data).hexdigest()
    return f"{algorithm}:{h}"


def short_id(obj: Any, length: int = 12) -> str:
    """Short content-derived ID useful for human display."""
    full = content_hash(obj)
    return full.split(":")[-1][:length]


def verify_hash(obj: Any, expected: str) -> bool:
    """Verify an object matches a previously recorded content hash."""
    return content_hash(obj) == expected


# Multi-node notes (for Phase 3+)
#
# - Each node stores objects keyed by content_hash.
# - Nodes can gossip new hashes + payloads out-of-band or via a shared index.
# - Critical receipts can optionally be anchored on-chain (tx hash recorded
#   in the Receipt itself).
# - No single node is authoritative; any node that has the content hash
#   can serve the object.
