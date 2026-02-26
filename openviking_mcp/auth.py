# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""API Key → MCP auth bridging."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from openviking.server.identity import ResolvedIdentity

if TYPE_CHECKING:
    from openviking.server.api_keys import APIKeyManager

logger = logging.getLogger("openviking-mcp.auth")


def resolve_identity(
    api_key_manager: Optional["APIKeyManager"],
    token: str,
) -> Optional[ResolvedIdentity]:
    """Resolve a Bearer token (API key) to an OpenViking identity.

    Returns None if auth is disabled (dev mode) or the key is invalid.
    """
    if api_key_manager is None:
        return None

    try:
        return api_key_manager.resolve(token)
    except Exception:
        return None
