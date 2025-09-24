"""
Simple Tools Handler

Handles basic Excel operations that return raw data for Claude to analyze.
"""

from typing import Dict, Any
from mcp.types import TextContent
from .base import BaseHandler
from ..simple_tools import (
    read_excel_region,
    search_in_excel,
    get_excel_info,
    calculate,
    show_excel_visual,
)


class SimpleToolsHandler(BaseHandler):
    """Handler for simple, Claude-driven intelligence tools."""

    async def handle_read_excel_region(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle read_excel_region tool call."""
        file_path = arguments.get("file_path")
        start_row = arguments.get("start_row")
        end_row = arguments.get("end_row")
        start_col = arguments.get("start_col")
        end_col = arguments.get("end_col")

        try:
            result = read_excel_region(
                file_path, start_row, end_row, start_col, end_col
            )
            output = "📊 Excel Region Data\n"
            output += f"Rows {start_row}-{end_row}, Columns {start_col}-{end_col}\n"
            output += "-" * 40 + "\n"
            for i, row in enumerate(result, start=start_row):
                output += f"Row {i}: {row}\n"
            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "read_excel_region")

    async def handle_search_in_excel(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle search_in_excel tool call."""
        file_path = arguments.get("file_path")
        search_term = arguments.get("search_term")
        case_sensitive = arguments.get("case_sensitive", False)

        try:
            results = search_in_excel(file_path, search_term, case_sensitive)
            output = f"🔍 Search Results for '{search_term}'\n"
            output += f"Found {len(results)} match(es)\n"
            output += "-" * 40 + "\n"
            for row, col, value in results[:20]:  # Limit to first 20
                output += f"Row {row}, Col {col}: {value}\n"
            if len(results) > 20:
                output += f"... and {len(results) - 20} more\n"
            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "search_in_excel")

    async def handle_get_excel_info(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle get_excel_info tool call."""
        file_path = arguments.get("file_path")

        try:
            info = get_excel_info(file_path)
            output = "📄 Excel File Information\n"
            output += "-" * 40 + "\n"
            output += f"File: {info['file_path']}\n"
            output += f"Rows: {info['rows']}\n"
            output += f"Columns: {info['columns']}\n"
            output += f"Sheets: {', '.join(info['sheets'])}\n"
            output += f"Size: {info['file_size_bytes']:,} bytes\n"
            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "get_excel_info")

    async def handle_calculate(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle calculate tool call."""
        operation = arguments.get("operation")
        values = arguments.get("values", [])

        try:
            result = calculate(operation, values)
            output = "🧮 Calculation Result\n"
            output += "-" * 40 + "\n"
            output += f"Operation: {operation}\n"
            output += f"Values: {values}\n"
            output += f"Result: {result}\n"
            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "calculate")

    async def handle_show_excel_visual(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle show_excel_visual tool call."""
        file_path = arguments.get("file_path")
        max_rows = arguments.get("max_rows", 20)
        max_cols = arguments.get("max_cols", 10)

        try:
            visual = show_excel_visual(file_path, max_rows, max_cols)
            return self.format_success(visual)
        except Exception as e:
            return self.format_error(str(e), "show_excel_visual")
