# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""FastMCP server factory and lifespan management."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Optional

from mcp.server.fastmcp import FastMCP

from openviking.server.api_keys import APIKeyManager
from openviking.service.core import OpenVikingService
from openviking_mcp.config import MCPServerConfig

logger = logging.getLogger("openviking-mcp")


@dataclass
class AppContext:
    """Shared application context available to all MCP tools."""

    service: OpenVikingService
    api_key_manager: Optional[APIKeyManager]


# Module-level reference so lifespan can access config set by create_mcp_server
_server_config: Optional[MCPServerConfig] = None


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize OpenVikingService on startup, clean up on shutdown."""
    config = _server_config or MCPServerConfig()

    service = OpenVikingService()
    await service.initialize()
    logger.info("OpenVikingService initialized")

    api_key_manager = None
    if config.root_api_key:
        api_key_manager = APIKeyManager(
            root_key=config.root_api_key,
            agfs_url=service._agfs_url,
        )
        await api_key_manager.load()
        logger.info("APIKeyManager initialized")
    else:
        logger.info("Dev mode: no root_api_key, authentication disabled")

    try:
        yield AppContext(service=service, api_key_manager=api_key_manager)
    finally:
        await service.close()
        logger.info("OpenVikingService closed")


def create_mcp_server(config: MCPServerConfig) -> FastMCP:
    """Create and configure the MCP server with all tools registered."""
    global _server_config
    _server_config = config

    mcp = FastMCP(
        name="openviking-mcp",
        instructions=(
            "OpenViking Context Database MCP Server. "
            "Provides tools for managing AI agent context: filesystem operations, "
            "semantic search, resource management, session/memory management, "
            "and more. All URIs use the viking:// protocol."
        ),
        host=config.host,
        port=config.port,
        stateless_http=True,
        json_response=True,
        lifespan=app_lifespan,
    )

    from openviking_mcp.tools import register_all_tools

    register_all_tools(mcp)

    return mcp
