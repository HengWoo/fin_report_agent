"""
Base Handler Class

Provides common functionality for all MCP tool handlers.
"""

import logging
from typing import Any, Dict
from mcp.types import TextContent


class BaseHandler:
    """Base class for all MCP tool handlers."""

    def __init__(self, server_context: Dict[str, Any]):
        """
        Initialize handler with server context.

        Args:
            server_context: Dictionary containing server components
                           (config, analytics_engine, parser, etc.)
        """
        self.context = server_context
        self.logger = logging.getLogger(self.__class__.__name__)

        # Extract common components from context
        self.config = server_context.get("config")
        self.analytics_engine = server_context.get("analytics_engine")
        self.adaptive_analyzer = server_context.get("adaptive_analyzer")
        self.parser = server_context.get("parser")
        self.hierarchy_parser = server_context.get("hierarchy_parser")
        self.validator = server_context.get("validator")
        self.tools = server_context.get("tools")

    def format_success(self, content: str) -> TextContent:
        """Format successful response."""
        return TextContent(type="text", text=content)

    def format_error(self, error: str, tool_name: str = None) -> TextContent:
        """Format error response."""
        prefix = f"❌ Error in {tool_name}: " if tool_name else "❌ Error: "
        return TextContent(type="text", text=f"{prefix}{error}")

    def log_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Log tool call for debugging."""
        self.logger.info(f"Tool called: {tool_name} with arguments: {arguments}")

    def log_tool_success(self, tool_name: str) -> None:
        """Log successful tool execution."""
        self.logger.info(f"Tool {tool_name} completed successfully")

    def log_tool_error(self, tool_name: str, error: Exception) -> None:
        """Log tool execution error."""
        self.logger.error(f"Error in tool {tool_name}: {str(error)}")
