# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Resource tools: resource_add, skill_add, wait_processed."""

from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import Context, FastMCP

from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_resource_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def resource_add(
        path: str,
        target: Optional[str] = None,
        reason: str = "",
        instruction: str = "",
        wait: bool = False,
        timeout: Optional[float] = None,
        ctx: Context = None,
    ) -> str:
        """Add a resource (file or URL) to the OpenViking knowledge base.

        Args:
            path: Resource path (local file path or URL)
            target: Target Viking URI (must be under viking://resources/)
            reason: Reason for adding this resource
            instruction: Processing instruction for the parser
            wait: Wait for semantic extraction and vectorization to complete
            timeout: Wait timeout in seconds (only used when wait=True)
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.resources.add_resource(
                path=path,
                ctx=request_ctx,
                target=target,
                reason=reason,
                instruction=instruction,
                wait=wait,
                timeout=timeout,
            )
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def skill_add(
        data: Any,
        wait: bool = False,
        timeout: Optional[float] = None,
        ctx: Context = None,
    ) -> str:
        """Add a skill definition to OpenViking.

        Args:
            data: Skill data (file path, string content, or dict/JSON)
            wait: Wait for vectorization to complete
            timeout: Wait timeout in seconds (only used when wait=True)
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            result = await app.service.resources.add_skill(
                data=data,
                ctx=request_ctx,
                wait=wait,
                timeout=timeout,
            )
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def wait_processed(
        timeout: Optional[float] = None, ctx: Context = None
    ) -> str:
        """Wait for all queued resource processing to complete.

        Args:
            timeout: Maximum wait time in seconds
        """
        try:
            app = get_app(ctx)
            result = await app.service.resources.wait_processed(timeout=timeout)
            return json.dumps(result, default=str)
        except OpenVikingError as e:
            return format_error(e)
