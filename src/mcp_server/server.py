"""
Restaurant Financial Analysis MCP Server (Refactored)

Streamlined MCP server using modular handler architecture.
"""

import logging
from typing import Optional

from mcp import Tool, Resource
from mcp.server import Server
from mcp.types import AnyUrl, TextContent

from .config import MCPServerConfig
from .handler_router import HandlerRouter
from .tool_registry import ToolRegistry
from .validation_state import validation_state_manager
from .financial_memory import financial_memory_manager
from .financial_navigator import financial_navigator
from .thinking_tools import thinking_tools
from ..analyzers.restaurant_analytics import RestaurantAnalyticsEngine
from ..analyzers.adaptive_financial_analyzer import AdaptiveFinancialAnalyzer
from ..parsers.account_hierarchy_parser import AccountHierarchyParser
from ..validators.restaurant_validator import RestaurantFinancialValidator


class RestaurantFinancialMCPServer:
    """MCP Server for Restaurant Financial Analysis."""

    def __init__(self, config: Optional[MCPServerConfig] = None):
        """Initialize the MCP server."""
        self.config = config or MCPServerConfig.from_env()
        self.server = Server(self.config.server_name)

        self.analytics_engine = RestaurantAnalyticsEngine()
        self.adaptive_analyzer = AdaptiveFinancialAnalyzer()
        self.hierarchy_parser = AccountHierarchyParser()
        self.validator = RestaurantFinancialValidator()

        self._setup_logging()

        server_context = {
            "logger": self.logger,
            "config": self.config,
            "analytics_engine": self.analytics_engine,
            "adaptive_analyzer": self.adaptive_analyzer,
            "hierarchy_parser": self.hierarchy_parser,
            "validator": self.validator,
            "validation_state_manager": validation_state_manager,
            "financial_memory_manager": financial_memory_manager,
            "financial_navigator": financial_navigator,
            "thinking_tools": thinking_tools,
        }

        self.router = HandlerRouter(server_context)

        self._register_handlers()

        self.logger.info(
            f"MCP Server initialized: {self.config.server_name} v{self.config.server_version}"
        )
        self.logger.info(
            f"Registered {len(self.router.get_available_tools())} tools across modular handlers"
        )

    def _setup_logging(self) -> None:
        """Setup logging configuration for MCP server (file-only to avoid stdio conflicts)."""
        self.logger = logging.getLogger(self.config.server_name)
        self.logger.setLevel(getattr(logging, self.config.log_level.upper()))

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        log_file = self.config.log_file or "mcp_server.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, self.config.log_level.upper()))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _register_handlers(self) -> None:
        """Register MCP handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return ToolRegistry.get_all_tools()

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            try:
                self.logger.info(f"Tool called: {name} with arguments: {arguments}")
                result = await self.router.route_tool_call(name, arguments)
                return [result] if result else []

            except Exception as e:
                self.logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
                error_msg = f"❌ Tool execution failed: {str(e)}"
                return [TextContent(type="text", text=error_msg)]

        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri=AnyUrl("memory://financial-patterns"),
                    name="Financial Patterns Memory",
                    description="Discovered financial patterns and domain knowledge",
                    mimeType="text/markdown",
                ),
                Resource(
                    uri=AnyUrl("memory://analysis-sessions"),
                    name="Analysis Sessions",
                    description="Historical analysis sessions and context",
                    mimeType="application/json",
                ),
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """Read resource content."""
            uri_str = str(uri)
            if uri_str == "memory://financial-patterns":
                return "# Financial Patterns\n\nStored patterns and insights..."
            elif uri_str == "memory://analysis-sessions":
                return '{"sessions": []}'
            else:
                raise ValueError(f"Unknown resource URI: {uri}")

    def run(self) -> None:
        """Run the MCP server."""
        self.logger.info("Starting MCP server...")
        import mcp.server.stdio

        mcp.server.stdio.run(self.server)
