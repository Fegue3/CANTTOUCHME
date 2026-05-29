# Canonical JSON helpers used for signing and hashing stable payloads.

import json
from typing import Any


def canonical_json_dumps(value: Any) -> str:
    # Serialize data with stable key ordering and compact separators.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_json_bytes(value: Any) -> bytes:
    # Return the canonical JSON representation encoded as UTF-8 bytes.
    return canonical_json_dumps(value).encode("utf-8")
