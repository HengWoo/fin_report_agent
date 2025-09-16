#!/usr/bin/env python3
"""
Restaurant Financial Analysis MCP Server

Main entry point for the Model Context Protocol (MCP) server
that provides restaurant financial analysis capabilities to Claude Code
and other AI systems.

Usage:
    python mcp_server_main.py [--config config.json] [--host localhost] [--port 8000]
"""

import asyncio
import argparse
import json
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from src.mcp_server.config import MCPServerConfig
from src.mcp_server.claude_integration import ClaudeCodeIntegration


class MCPServerManager:
    """Manager for the MCP server lifecycle."""

    def __init__(self, config: MCPServerConfig):
        """Initialize the server manager."""
        self.config = config
        self.claude_integration: Optional[ClaudeCodeIntegration] = None
        self.running = False

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                *([logging.FileHandler(self.config.log_file)] if self.config.log_file else [])
            ]
        )
        self.logger = logging.getLogger("mcp_server_manager")

    async def start(self) -> None:
        """Start the MCP server."""
        self.logger.info("Starting Restaurant Financial Analysis MCP Server")
        self.logger.info(f"Server: {self.config.server_name} v{self.config.server_version}")
        self.logger.info(f"Host: {self.config.host}:{self.config.port}")

        try:
            # Initialize Claude Code integration
            self.claude_integration = ClaudeCodeIntegration(self.config)
            await self.claude_integration.initialize()

            self.running = True
            self.logger.info("MCP Server started successfully")

            # Keep the server running
            await self._run_server()

        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {str(e)}")
            raise

    async def _run_server(self) -> None:
        """Run the server main loop."""
        self.logger.info("MCP Server is running. Press Ctrl+C to stop.")

        try:
            # In a real MCP implementation, this would handle the MCP protocol
            # For now, we'll just keep the server alive
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
            raise

    async def stop(self) -> None:
        """Stop the MCP server."""
        self.logger.info("Stopping MCP Server")

        try:
            self.running = False

            if self.claude_integration:
                await self.claude_integration.shutdown()

            self.logger.info("MCP Server stopped successfully")

        except Exception as e:
            self.logger.error(f"Error during server shutdown: {str(e)}")
            raise

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle system signals."""
        self.logger.info(f"Received signal {signum}")
        asyncio.create_task(self.stop())


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Restaurant Financial Analysis MCP Server"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (JSON format)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Server host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path (optional)"
    )
    parser.add_argument(
        "--bilingual",
        action="store_true",
        default=True,
        help="Enable bilingual output (default: True)"
    )

    args = parser.parse_args()

    # Load configuration
    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        config = MCPServerConfig(**config_data)
    else:
        # Use command line arguments and environment variables
        config = MCPServerConfig.from_env()

    # Override with command line arguments
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port
    if args.log_level:
        config.log_level = args.log_level
    if args.log_file:
        config.log_file = args.log_file
    if args.bilingual is not None:
        config.enable_bilingual_output = args.bilingual

    # Create and start server manager
    server_manager = MCPServerManager(config)

    # Setup signal handlers
    signal.signal(signal.SIGINT, server_manager._signal_handler)
    signal.signal(signal.SIGTERM, server_manager._signal_handler)

    try:
        await server_manager.start()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    except Exception as e:
        print(f"Server failed: {str(e)}")
        sys.exit(1)
    finally:
        await server_manager.stop()


def demo_mode() -> None:
    """Run server in demonstration mode."""
    print("🏪 Restaurant Financial Analysis MCP Server")
    print("=" * 60)
    print()
    print("🚀 Demo Mode - Showcasing MCP Server Capabilities")
    print()

    # Display server capabilities
    print("📊 Available Tools:")
    tools = [
        ("parse_excel", "Parse Chinese restaurant Excel financial statements"),
        ("validate_financial_data", "Validate financial data against industry standards"),
        ("calculate_kpis", "Calculate restaurant KPIs and performance metrics"),
        ("analyze_trends", "Perform trend analysis on historical data"),
        ("generate_insights", "Generate business insights and recommendations"),
        ("comprehensive_analysis", "Complete end-to-end financial analysis")
    ]

    for tool_name, description in tools:
        print(f"   • {tool_name}: {description}")

    print()
    print("🌐 Language Support:")
    print("   • English (en)")
    print("   • Chinese (zh)")
    print("   • Bilingual output (both)")

    print()
    print("🔧 Integration Features:")
    print("   • Claude Code MCP Protocol support")
    print("   • Real-time financial analysis")
    print("   • Industry benchmark comparisons")
    print("   • Automated insight generation")
    print("   • Bilingual report generation")

    print()
    print("🚀 Server ready for Claude Code integration!")
    print("   Use 'python mcp_server_main.py' to start the server")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        asyncio.run(main())