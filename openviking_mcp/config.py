# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""MCP server configuration."""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MCPServerConfig:
    """Configuration for the OpenViking MCP server."""

    host: str = "0.0.0.0"
    port: int = 2033
    root_api_key: Optional[str] = None
    cors_origins: list = field(default_factory=lambda: ["*"])

    @classmethod
    def from_ov_conf(cls, config_path: str) -> "MCPServerConfig":
        """Load config from ov.conf, merging server and mcp_server sections."""
        if not os.path.exists(config_path):
            return cls()

        with open(config_path, "r") as f:
            data = json.load(f)

        server = data.get("server", {})
        mcp = data.get("mcp_server", {})

        return cls(
            host=mcp.get("host", server.get("host", "0.0.0.0")),
            port=mcp.get("port", 2033),
            root_api_key=mcp.get("root_api_key", server.get("root_api_key")),
            cors_origins=mcp.get("cors_origins", server.get("cors_origins", ["*"])),
        )
