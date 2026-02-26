# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Tool registration hub."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Register all OpenViking MCP tools."""
    from openviking_mcp.tools.system import register_system_tools

    register_system_tools(mcp)

    # Phase 3: core tools
    from openviking_mcp.tools.content import register_content_tools
    from openviking_mcp.tools.filesystem import register_fs_tools
    from openviking_mcp.tools.resources import register_resource_tools
    from openviking_mcp.tools.search import register_search_tools

    register_fs_tools(mcp)
    register_content_tools(mcp)
    register_search_tools(mcp)
    register_resource_tools(mcp)

    # Phase 4: session + relation tools
    from openviking_mcp.tools.relations import register_relation_tools
    from openviking_mcp.tools.sessions import register_session_tools

    register_session_tools(mcp)
    register_relation_tools(mcp)

    # Phase 5: admin + pack tools
    from openviking_mcp.tools.admin import register_admin_tools
    from openviking_mcp.tools.pack import register_pack_tools

    register_admin_tools(mcp)
    register_pack_tools(mcp)
