# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Pack tools: pack_export, pack_import."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP

from openviking_cli.exceptions import OpenVikingError
from openviking_mcp.context import get_app, get_request_context
from openviking_mcp.errors import format_error


def register_pack_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    async def pack_export(uri: str, to: str, ctx: Context = None) -> str:
        """Export a Viking resource subtree as an .ovpack file.

        Args:
            uri: Viking URI to export
            to: Local file path for the .ovpack output
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            file_path = await app.service.pack.export_ovpack(uri, to, ctx=request_ctx)
            return json.dumps({"file": file_path})
        except OpenVikingError as e:
            return format_error(e)

    @mcp.tool()
    async def pack_import(
        file_path: str,
        parent: str,
        force: bool = False,
        vectorize: bool = True,
        ctx: Context = None,
    ) -> str:
        """Import an .ovpack file into the Viking filesystem.

        Args:
            file_path: Local path to the .ovpack file
            parent: Target parent Viking URI (e.g. "viking://resources/references/")
            force: Overwrite existing resources
            vectorize: Trigger vectorization after import
        """
        try:
            app = get_app(ctx)
            request_ctx = get_request_context(ctx)
            uri = await app.service.pack.import_ovpack(
                file_path, parent, ctx=request_ctx, force=force, vectorize=vectorize
            )
            return json.dumps({"uri": uri})
        except OpenVikingError as e:
            return format_error(e)
