# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""MCP Context → OpenViking RequestContext conversion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openviking.server.identity import RequestContext, Role
from openviking_cli.session.user_id import UserIdentifier

if TYPE_CHECKING:
    from mcp.server.fastmcp import Context

    from openviking_mcp.server import AppContext


def get_app(ctx: Context) -> AppContext:
    """Extract AppContext from MCP tool Context."""
    return ctx.request_context.lifespan_context


def get_request_context(ctx: Context) -> RequestContext:
    """Build a RequestContext from MCP tool Context.

    In authenticated mode, the identity is resolved during auth and stored
    in the MCP session. In dev mode (no root_api_key), returns a default
    ROOT context.
    """
    app = get_app(ctx)

    # Try to get identity from session metadata (set by auth middleware)
    session = ctx.request_context.session
    identity = getattr(session, "_ov_identity", None)

    if identity is not None:
        return RequestContext(
            user=UserIdentifier(
                identity.account_id or "default",
                identity.user_id or "default",
                identity.agent_id or "default",
            ),
            role=identity.role,
        )

    # Dev mode: no auth configured, return default ROOT context
    return RequestContext(
        user=UserIdentifier("default", "default", "default"),
        role=Role.ROOT,
    )
