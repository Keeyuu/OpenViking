# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Search tools: find, search, grep, glob."""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import Context, FastMCP

from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_search_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def search_find(
        query: str,
        target_uri: str = "",
        limit: int = 10,
        score_threshold: Optional[float] = None,
        ctx: Context = None,
    ) -> str:
        """Semantic search without session context.

        Args:
            query: Natural language query
            target_uri: Restrict search to this URI subtree
            limit: Maximum number of results
            score_threshold: Minimum relevance score (0.0-1.0)
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.search.find(
                query=query,
                ctx=request_ctx,
                target_uri=target_uri,
                limit=limit,
                score_threshold=score_threshold,
            )
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def search_search(
        query: str,
        target_uri: str = "",
        session_id: Optional[str] = None,
        limit: int = 10,
        score_threshold: Optional[float] = None,
        ctx: Context = None,
    ) -> str:
        """Semantic search with optional session context for better relevance.

        Args:
            query: Natural language query
            target_uri: Restrict search to this URI subtree
            session_id: Session ID for contextual search
            limit: Maximum number of results
            score_threshold: Minimum relevance score (0.0-1.0)
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)

            session = None
            if session_id:
                session = app.service.sessions.session(request_ctx, session_id)
                await session.load()

            result = await app.service.search.search(
                query=query,
                ctx=request_ctx,
                target_uri=target_uri,
                session=session,
                limit=limit,
                score_threshold=score_threshold,
            )
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def search_grep(
        uri: str,
        pattern: str,
        case_insensitive: bool = False,
        ctx: Context = None,
    ) -> str:
        """Pattern-based content search (like grep).

        Args:
            uri: Viking URI to search within
            pattern: Search pattern (regex supported)
            case_insensitive: Ignore case when matching
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.grep(
                uri, pattern, ctx=request_ctx, case_insensitive=case_insensitive
            )
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def search_glob(
        pattern: str, uri: str = "viking://", ctx: Context = None
    ) -> str:
        """File pattern matching (like glob).

        Args:
            pattern: Glob pattern (e.g. "*.md", "**/*.py")
            uri: Base URI to search from
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.fs.glob(pattern, ctx=request_ctx, uri=uri)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)
