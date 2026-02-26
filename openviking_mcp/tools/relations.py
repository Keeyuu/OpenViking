# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Relation tools: relation_list, relation_link, relation_unlink."""

from __future__ import annotations

import json
from typing import List, Union

from mcp.server.fastmcp import Context, FastMCP

from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_relation_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def relation_list(uri: str, ctx: Context = None) -> str:
        """List all relations for a resource.

        Args:
            uri: Viking URI of the resource
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.relations.relations(uri, ctx=request_ctx)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def relation_link(
        from_uri: str,
        to_uris: Union[str, List[str]],
        reason: str = "",
        ctx: Context = None,
    ) -> str:
        """Create a link between resources.

        Args:
            from_uri: Source Viking URI
            to_uris: Target Viking URI or list of URIs
            reason: Reason for linking
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            await app.service.relations.link(
                from_uri, to_uris, ctx=request_ctx, reason=reason
            )
            return json.dumps({"from": from_uri, "to": to_uris})
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def relation_unlink(
        from_uri: str, uri: str, ctx: Context = None
    ) -> str:
        """Remove a link between resources.

        Args:
            from_uri: Source Viking URI
            uri: Target Viking URI to unlink
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            await app.service.relations.unlink(from_uri, uri, ctx=request_ctx)
            return json.dumps({"from": from_uri, "to": uri})
        except OpenVikingError as e:
            return format_error(e)
