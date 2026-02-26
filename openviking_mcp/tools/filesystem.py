# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Filesystem tools: ls, tree, stat, mkdir, rm, mv."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP

from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_fs_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def fs_ls(
        uri: str,
        simple: bool = False,
        recursive: bool = False,
        output: str = "agent",
        abs_limit: int = 256,
        show_all_hidden: bool = False,
        node_limit: int = 1000,
        ctx: Context = None,
    ) -> str:
        """List directory contents in the Viking filesystem.

        Args:
            uri: Viking URI (e.g. "viking://resources/")
            simple: Return only relative path list
            recursive: List all subdirectories recursively
            output: Output format - "original" or "agent"
            abs_limit: Abstract character limit (agent output only)
            show_all_hidden: Show hidden files
            node_limit: Maximum nodes to list
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.ls(
                uri,
                ctx=request_ctx,
                recursive=recursive,
                simple=simple,
                output=output,
                abs_limit=abs_limit,
                show_all_hidden=show_all_hidden,
                node_limit=node_limit,
            )
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def fs_tree(
        uri: str,
        output: str = "agent",
        abs_limit: int = 128,
        show_all_hidden: bool = False,
        node_limit: int = 1000,
        ctx: Context = None,
    ) -> str:
        """Get directory tree structure.

        Args:
            uri: Viking URI
            output: Output format - "original" or "agent"
            abs_limit: Abstract character limit (agent output only)
            show_all_hidden: Show hidden files
            node_limit: Maximum nodes to list
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.tree(
                uri,
                ctx=request_ctx,
                output=output,
                abs_limit=abs_limit,
                show_all_hidden=show_all_hidden,
                node_limit=node_limit,
            )
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def fs_stat(uri: str, ctx: Context = None) -> str:
        """Get file or directory metadata (size, type, timestamps, etc.).

        Args:
            uri: Viking URI
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.stat(uri, ctx=request_ctx)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def fs_mkdir(uri: str, ctx: Context = None) -> str:
        """Create a directory in the Viking filesystem.

        Args:
            uri: Viking URI for the new directory
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            await app.service.fs.mkdir(uri, ctx=request_ctx)
            return json.dumps({"uri": uri})
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def fs_rm(uri: str, recursive: bool = False, ctx: Context = None) -> str:
        """Remove a file or directory from the Viking filesystem.

        Args:
            uri: Viking URI to remove
            recursive: Remove directory and all contents recursively
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            await app.service.fs.rm(uri, ctx=request_ctx, recursive=recursive)
            return json.dumps({"uri": uri})
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def fs_mv(from_uri: str, to_uri: str, ctx: Context = None) -> str:
        """Move or rename a file/directory in the Viking filesystem.

        Args:
            from_uri: Source Viking URI
            to_uri: Destination Viking URI
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            await app.service.fs.mv(from_uri, to_uri, ctx=request_ctx)
            return json.dumps({"from": from_uri, "to": to_uri})
        except OpenVikingError as e:
            return format_error(e)
