# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""Error handling utilities for MCP tools."""

import json

from openviking_cli.exceptions import OpenVikingError


def format_error(e: OpenVikingError) -> str:
    """Convert OpenVikingError to a JSON error string for MCP tool response."""
    return json.dumps(
        {"error": True, "code": e.code, "message": e.message, "details": e.details},
        default=str,
    )


def permission_denied(message: str = "Permission denied") -> str:
    """Return a permission denied error response."""
    return json.dumps({"error": True, "code": "PERMISSION_DENIED", "message": message})
