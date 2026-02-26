# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Session tools: create, list, get, delete, commit, extract, add_message."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP

from openviking.message.part import TextPart, part_from_dict
from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_session_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def session_create(ctx: Context = None) -> str:
        """Create a new conversation session.

        Returns session_id and user info.
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            await app.service.initialize_user_directories(request_ctx)
            await app.service.initialize_agent_directories(request_ctx)
            session = await app.service.sessions.create(request_ctx)
            return json.dumps(
                {"session_id": session.session_id, "user": str(request_ctx.user)}
            )
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def session_list(ctx: Context = None) -> str:
        """List all sessions for the current user."""
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.sessions.sessions(request_ctx)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def session_get(session_id: str, ctx: Context = None) -> str:
        """Get session details.

        Args:
            session_id: Session ID to retrieve
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            session = await app.service.sessions.get(session_id, request_ctx)
            return json.dumps(
                {
                    "session_id": session.session_id,
                    "user": str(request_ctx.user),
                    "message_count": len(session.messages),
                },
                default=str,
            )
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def session_delete(session_id: str, ctx: Context = None) -> str:
        """Delete a session.

        Args:
            session_id: Session ID to delete
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            await app.service.sessions.delete(session_id, request_ctx)
            return json.dumps({"session_id": session_id, "deleted": True})
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def session_commit(session_id: str, ctx: Context = None) -> str:
        """Commit a session — archive messages and extract memories.

        Args:
            session_id: Session ID to commit
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.sessions.commit(session_id, request_ctx)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def session_extract(session_id: str, ctx: Context = None) -> str:
        """Extract long-term memories from a session.

        Args:
            session_id: Session ID to extract memories from
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.sessions.extract(session_id, request_ctx)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def session_add_message(
        session_id: str,
        role: str,
        content: Optional[str] = None,
        parts: Optional[List[Dict[str, Any]]] = None,
        ctx: Context = None,
    ) -> str:
        """Add a message to a session.

        Args:
            session_id: Target session ID
            role: Message role ("user", "assistant", "system")
            content: Simple text content (use this OR parts, not both)
            parts: Structured message parts list. Each part is a dict with "type" key:
                   - {"type": "text", "text": "..."}
                   - {"type": "context", "uri": "...", "context_type": "memory|resource|skill", "abstract": "..."}
                   - {"type": "tool", "tool_id": "...", "tool_name": "...", ...}
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            session = app.service.sessions.session(request_ctx, session_id)
            await session.load()

            if content is not None:
                msg_parts = [TextPart(text=content)]
            elif parts is not None:
                msg_parts = [part_from_dict(p) for p in parts]
            else:
                return json.dumps(
                    {
                        "error": True,
                        "code": "INVALID_ARGUMENT",
                        "message": "Either content or parts must be provided",
                    }
                )

            session.add_message(role, msg_parts)
            return json.dumps(
                {
                    "session_id": session_id,
                    "message_count": len(session.messages),
                }
            )
        except OpenVikingError as e:
            return format_error(e)
