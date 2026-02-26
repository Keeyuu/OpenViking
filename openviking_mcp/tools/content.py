# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Content tools: read, abstract, overview."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP

from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_content_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def content_read(
        uri: str, offset: int = 0, limit: int = -1, ctx: Context = None
    ) -> str:
        """Read full content (L2) of a resource.

        Args:
            uri: Viking URI of the resource
            offset: Starting line number (0-indexed)
            limit: Number of lines to read (-1 means read to end)
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.read(
                uri, ctx=request_ctx, offset=offset, limit=limit
            )
            return result if isinstance(result, str) else json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def content_abstract(uri: str, ctx: Context = None) -> str:
        """Read L0 abstract of a resource (short summary).

        Args:
            uri: Viking URI of the resource
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.abstract(uri, ctx=request_ctx)
            return result if isinstance(result, str) else json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def content_overview(uri: str, ctx: Context = None) -> str:
        """Read L1 overview of a resource (structured summary).

        Args:
            uri: Viking URI of the resource
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.overview(uri, ctx=request_ctx)
            return result if isinstance(result, str) else json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)
