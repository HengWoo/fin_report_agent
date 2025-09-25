#!/usr/bin/env python3
"""
MCP Server Startup Script for Claude Code Integration

Run this to start the Restaurant Financial Analysis MCP server
that Claude Code can connect to.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server.server import RestaurantFinancialMCPServer
from src.mcp_server.config import MCPServerConfig


async def main():
    """Start the MCP server for Claude Code integration."""
    # NO logging.basicConfig() to avoid stdout interference with MCP stdio

    # Create configuration
    config = MCPServerConfig(
        server_name="fin-report-agent",
        server_version="1.0.0",
        enable_bilingual_output=True,
        log_level="INFO"  # Server will log to file only
    )

    # Initialize server
    mcp_server = RestaurantFinancialMCPServer(config)

    # Get the underlying MCP server and run with stdio transport
    from mcp import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            mcp_server.server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())