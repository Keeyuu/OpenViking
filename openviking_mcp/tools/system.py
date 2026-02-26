# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""System and observer tools."""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import Context, FastMCP

from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_system_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def system_health(ctx: Context) -> str:
        """Check if the OpenViking service is healthy."""
        try:
            app = get_app(ctx)
            healthy = app.service.debug.is_healthy()
            return json.dumps({"healthy": healthy})
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def system_status(ctx: Context) -> str:
        """Get the current system status including initialization state and user info."""
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            return json.dumps(
                {
                    "initialized": app.service._initialized,
                    "user": str(request_ctx.user),
                    "role": request_ctx.role.value,
                }
            )
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def observer_status(component: Optional[str] = None, ctx: Context = None) -> str:
        """Get observer status for system components.

        Args:
            component: Component name (queue, vikingdb, vlm, transaction).
                       If omitted, returns full system status.
        """
        try:
            app = get_app(ctx)
            observer = app.service.debug.observer

            if component is None:
                result = observer.system
            elif component == "queue":
                result = observer.queue
            elif component == "vikingdb":
                result = observer.vikingdb
            elif component == "vlm":
                result = observer.vlm
            elif component == "transaction":
                result = observer.transaction
            else:
                return json.dumps(
                    {
                        "error": True,
                        "code": "INVALID_ARGUMENT",
                        "message": f"Unknown component: {component}. "
                        "Valid: queue, vikingdb, vlm, transaction",
                    }
                )

            if hasattr(result, "__dict__"):
                return json.dumps(result.__dict__, default=str)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)
