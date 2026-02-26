# Copyright (c) 2026 OpenViking Contributors
# SPDX-License-Identifier: Apache-2.0
"""CLI entry point for the OpenViking MCP server."""

import argparse
import logging
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenViking MCP Server — expose OpenViking capabilities via MCP",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=os.getenv("OPENVIKING_CONFIG_FILE", os.path.expanduser("~/.openviking/ov.conf")),
        help="Path to ov.conf (default: ~/.openviking/ov.conf)",
    )
    parser.add_argument("--host", type=str, default=None, help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Port to listen on (default: 2033)")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["streamable-http", "stdio"],
        default="streamable-http",
        help="Transport type (default: streamable-http)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if os.getenv("OV_DEBUG") == "1":
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("openviking-mcp")

    # Set config file env var so OpenVikingService picks it up
    os.environ.setdefault("OPENVIKING_CONFIG_FILE", args.config)

    from openviking_mcp.config import MCPServerConfig
    from openviking_mcp.server import create_mcp_server

    config = MCPServerConfig.from_ov_conf(args.config)

    # CLI overrides
    if args.host is not None:
        config.host = args.host
    if args.port is not None:
        config.port = args.port

    logger.info("OpenViking MCP Server starting")
    logger.info("  config: %s", args.config)
    logger.info("  transport: %s", args.transport)

    mcp = create_mcp_server(config)

    if args.transport == "streamable-http":
        logger.info("  endpoint: http://%s:%d/mcp", config.host, config.port)
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
