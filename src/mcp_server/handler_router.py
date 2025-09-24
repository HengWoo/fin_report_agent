"""
Handler Router

Routes MCP tool calls to appropriate handler instances.
"""

from typing import Dict, Any, Optional
from mcp.types import TextContent

from .handlers.simple_tools_handler import SimpleToolsHandler
from .handlers.navigation_handler import NavigationHandler
from .handlers.thinking_handler import ThinkingHandler
from .handlers.memory_handler import MemoryHandler
from .handlers.legacy_analysis_handler import LegacyAnalysisHandler
from .handlers.complex_analysis_handler import ComplexAnalysisHandler


class HandlerRouter:
    """Routes tool calls to appropriate handlers."""

    def __init__(self, server_context: Dict[str, Any]):
        """Initialize router with handler instances."""
        self.simple_tools = SimpleToolsHandler(server_context)
        self.navigation = NavigationHandler(server_context)
        self.thinking = ThinkingHandler(server_context)
        self.memory = MemoryHandler(server_context)
        self.legacy_analysis = LegacyAnalysisHandler(server_context)
        self.complex_analysis = ComplexAnalysisHandler(server_context)

        self.tool_to_handler = {
            "read_excel_region": self.simple_tools.handle_read_excel_region,
            "search_in_excel": self.simple_tools.handle_search_in_excel,
            "get_excel_info": self.simple_tools.handle_get_excel_info,
            "calculate": self.simple_tools.handle_calculate,
            "show_excel_visual": self.simple_tools.handle_show_excel_visual,
            "find_account": self.navigation.handle_find_account,
            "get_financial_overview": self.navigation.handle_get_financial_overview,
            "get_account_context": self.navigation.handle_get_account_context,
            "think_about_financial_data": self.thinking.handle_think_about_financial_data,
            "think_about_analysis_completeness": self.thinking.handle_think_about_analysis_completeness,
            "think_about_assumptions": self.thinking.handle_think_about_assumptions,
            "save_analysis_insight": self.memory.handle_save_analysis_insight,
            "get_session_context": self.memory.handle_get_session_context,
            "write_memory_note": self.memory.handle_write_memory_note,
            "parse_excel": self.legacy_analysis.handle_parse_excel,
            "validate_financial_data": self.legacy_analysis.handle_validate_financial_data,
            "calculate_kpis": self.legacy_analysis.handle_calculate_kpis,
            "analyze_trends": self.legacy_analysis.handle_analyze_trends,
            "generate_insights": self.legacy_analysis.handle_generate_insights,
            "comprehensive_analysis": self.complex_analysis.handle_comprehensive_analysis,
            "adaptive_financial_analysis": self.complex_analysis.handle_adaptive_financial_analysis,
            "validate_account_structure": self.complex_analysis.handle_validate_account_structure,
        }

    async def route_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Optional[TextContent]:
        """Route a tool call to the appropriate handler."""
        handler = self.tool_to_handler.get(tool_name)

        if not handler:
            return TextContent(
                type="text",
                text=f"❌ Unknown tool: {tool_name}\n\nAvailable tools: {', '.join(self.tool_to_handler.keys())}",
            )

        try:
            return await handler(arguments)
        except Exception as e:
            return TextContent(
                type="text",
                text=f"❌ Error executing {tool_name}: {str(e)}\n\nPlease check the tool arguments and try again.",
            )

    def get_available_tools(self) -> list[str]:
        """Get list of all available tool names."""
        return list(self.tool_to_handler.keys())

    def get_handler_for_tool(self, tool_name: str) -> Optional[str]:
        """Get the handler class name for a given tool."""
        handler = self.tool_to_handler.get(tool_name)
        if handler:
            return handler.__self__.__class__.__name__
        return None