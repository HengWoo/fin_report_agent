"""
Tool Registry

Centralized tool definitions and metadata for the MCP server.
"""

from typing import List
from mcp import Tool


class ToolRegistry:
    """Registry for all MCP tools with organized categories."""

    @staticmethod
    def get_simple_tools() -> List[Tool]:
        """Get simple, Claude-driven intelligence tools."""
        return [
            Tool(
                name="read_excel_region",
                description="Extract a rectangular region of cells from Excel. Returns raw data with no interpretation. Let Claude decide what it means.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        },
                        "start_row": {
                            "type": "integer",
                            "description": "Starting row (0-indexed)",
                        },
                        "end_row": {
                            "type": "integer",
                            "description": "Ending row (inclusive)",
                        },
                        "start_col": {
                            "type": "integer",
                            "description": "Starting column (0-indexed)",
                        },
                        "end_col": {
                            "type": "integer",
                            "description": "Ending column (inclusive)",
                        },
                    },
                    "required": [
                        "file_path",
                        "start_row",
                        "end_row",
                        "start_col",
                        "end_col",
                    ],
                },
            ),
            Tool(
                name="search_in_excel",
                description="Find all cells containing a search term. Returns locations and values. Claude interprets what the matches mean.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        },
                        "search_term": {
                            "type": "string",
                            "description": "Text to search for",
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Match case (default: false)",
                        },
                    },
                    "required": ["file_path", "search_term"],
                },
            ),
            Tool(
                name="get_excel_info",
                description="Get basic Excel file structure: rows, columns, sheet names. No interpretation, just dimensions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        }
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="calculate",
                description="Perform simple math: sum, average, max, min. Claude decides what to calculate, tool just does the math.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "One of: sum, average, max, min",
                        },
                        "values": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "List of numbers",
                        },
                    },
                    "required": ["operation", "values"],
                },
            ),
            Tool(
                name="show_excel_visual",
                description="Display Excel in readable format for Claude to analyze. Shows raw data with row/column labels.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        },
                        "max_rows": {
                            "type": "integer",
                            "description": "Max rows to show (default: 20)",
                        },
                        "max_cols": {
                            "type": "integer",
                            "description": "Max columns to show (default: 10)",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
        ]

    @staticmethod
    def get_navigation_tools() -> List[Tool]:
        """Get LSP-like financial navigation tools."""
        return [
            Tool(
                name="find_account",
                description="Search for financial accounts by name pattern (like LSP find_symbol). Supports Chinese/English terms and hierarchical navigation.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        },
                        "name_pattern": {
                            "type": "string",
                            "description": "Account name or pattern to search for",
                        },
                        "exact_match": {
                            "type": "boolean",
                            "description": "Exact match only (default: false)",
                        },
                        "account_type": {
                            "type": "string",
                            "description": "Filter by type: asset, liability, revenue, expense, etc.",
                        },
                    },
                    "required": ["file_path", "name_pattern"],
                },
            ),
            Tool(
                name="get_financial_overview",
                description="Get high-level financial structure overview (like LSP symbols overview). Shows top-level accounts and hierarchy.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum hierarchy depth to show (default: 2)",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="get_account_context",
                description="Get account with surrounding context - parent, children, siblings (like reading code with context lines).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        },
                        "account_name_path": {
                            "type": "string",
                            "description": "Full account name path",
                        },
                        "depth": {
                            "type": "integer",
                            "description": "Context depth (default: 1)",
                        },
                    },
                    "required": ["file_path", "account_name_path"],
                },
            ),
        ]

    @staticmethod
    def get_thinking_tools() -> List[Tool]:
        """Get thinking and reflection tools."""
        return [
            Tool(
                name="think_about_financial_data",
                description="Reflect on collected financial data and assess if enough information has been gathered for analysis. Returns recommendations for next steps.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "collected_data": {
                            "type": "object",
                            "description": "Summary of data collected so far",
                        },
                        "analysis_goal": {
                            "type": "string",
                            "description": "The analysis goal or objective",
                        },
                    },
                    "required": ["collected_data", "analysis_goal"],
                },
            ),
            Tool(
                name="think_about_analysis_completeness",
                description="Check if financial analysis is complete against requirements. Identifies missing components.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_performed": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of completed analysis steps",
                        },
                        "required_components": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of required components",
                        },
                    },
                    "required": ["analysis_performed", "required_components"],
                },
            ),
            Tool(
                name="think_about_assumptions",
                description="Validate financial assumptions against context and best practices. Ensures assumptions are documented and reasonable.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assumptions": {
                            "type": "object",
                            "description": "Assumptions made during analysis",
                        },
                        "financial_context": {
                            "type": "object",
                            "description": "Financial context for validation",
                        },
                    },
                    "required": ["assumptions", "financial_context"],
                },
            ),
        ]

    @staticmethod
    def get_memory_tools() -> List[Tool]:
        """Get memory and session management tools."""
        return [
            Tool(
                name="save_analysis_insight",
                description="Save a discovered insight or pattern to memory for future reference. Builds knowledge across sessions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Current session ID",
                        },
                        "key": {"type": "string", "description": "Insight key/identifier"},
                        "description": {
                            "type": "string",
                            "description": "Insight description",
                        },
                        "insight_type": {
                            "type": "string",
                            "description": "Type: pattern, anomaly, recommendation, etc.",
                        },
                        "context": {"type": "object", "description": "Context data"},
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level 0.0-1.0 (default: 0.8)",
                        },
                    },
                    "required": [
                        "session_id",
                        "key",
                        "description",
                        "insight_type",
                        "context",
                    ],
                },
            ),
            Tool(
                name="get_session_context",
                description="Get analysis session context and history. Shows what's been done in current session.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"}
                    },
                    "required": ["session_id"],
                },
            ),
            Tool(
                name="write_memory_note",
                description="Write a memory note about financial patterns or domain knowledge (like Serena's memory files).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Memory note name"},
                        "content": {
                            "type": "string",
                            "description": "Memory content in markdown format",
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional session ID to associate",
                        },
                    },
                    "required": ["name", "content"],
                },
            ),
        ]

    @staticmethod
    def get_legacy_tools() -> List[Tool]:
        """Get legacy financial analysis tools."""
        return [
            Tool(
                name="parse_excel",
                description="Parse Chinese restaurant Excel files into structured financial data. Uses AccountHierarchyParser with column intelligence to prevent double counting.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file",
                        },
                        "sheet_name": {
                            "type": "string",
                            "description": "Sheet name (optional)",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="validate_financial_data",
                description="Validate restaurant financial data against industry standards and business rules",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "financial_data": {
                            "type": "object",
                            "description": "Financial data to validate (income statement format)",
                        },
                        "strict_mode": {
                            "type": "boolean",
                            "description": "Enable strict validation mode (default: false)",
                        },
                    },
                    "required": ["financial_data"],
                },
            ),
            Tool(
                name="calculate_kpis",
                description="Calculate restaurant KPIs and performance metrics from financial data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "income_statement": {
                            "type": "object",
                            "description": "Income statement data for KPI calculation",
                        },
                        "include_benchmarks": {
                            "type": "boolean",
                            "description": "Include industry benchmark comparisons (default: true)",
                        },
                    },
                    "required": ["income_statement"],
                },
            ),
            Tool(
                name="analyze_trends",
                description="Perform trend analysis on historical restaurant financial data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "historical_statements": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Array of historical income statements",
                        },
                        "include_forecasting": {
                            "type": "boolean",
                            "description": "Include future trend forecasting (default: true)",
                        },
                    },
                    "required": ["historical_statements"],
                },
            ),
            Tool(
                name="generate_insights",
                description="Generate business insights and recommendations from restaurant data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kpis": {
                            "type": "object",
                            "description": "Restaurant KPIs data",
                        },
                        "income_statement": {
                            "type": "object",
                            "description": "Income statement data",
                        },
                        "language": {
                            "type": "string",
                            "description": "Output language (en/zh/both, default: both)",
                        },
                    },
                    "required": ["kpis", "income_statement"],
                },
            ),
        ]

    @staticmethod
    def get_complex_tools() -> List[Tool]:
        """Get complex analysis workflow tools."""
        return [
            Tool(
                name="comprehensive_analysis",
                description="Perform comprehensive financial analysis using Claude Orchestrator. Includes parsing, validation, KPI calculation, trends, and insights in one workflow.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file to analyze",
                        },
                        "language": {
                            "type": "string",
                            "description": "Output language (en/zh/both, default: both)",
                        },
                        "include_executive_summary": {
                            "type": "boolean",
                            "description": "Include executive summary (default: true)",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="adaptive_financial_analysis",
                description="Intelligent financial analysis that adapts to any Excel format. Uses AI agents to understand structure and perform context-aware analysis.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file to analyze",
                        },
                        "analysis_focus": {
                            "type": "string",
                            "enum": ["profitability", "growth", "efficiency", "comprehensive"],
                            "description": "Focus area: 'profitability', 'growth', 'efficiency', or 'comprehensive' (default: comprehensive)",
                        },
                        "business_context": {
                            "type": "string",
                            "description": "Optional business context (e.g., 'new_location', 'seasonal_business', 'chain_restaurant')",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="validate_account_structure",
                description="MANDATORY first step: Parse Excel and extract account hierarchy for validation. Shows parent-child relationships and asks user to confirm structure before any calculations.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to Excel file to analyze",
                        },
                        "show_details": {
                            "type": "boolean",
                            "description": "Show detailed account breakdown (default: true)",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
        ]

    @staticmethod
    def get_all_tools() -> List[Tool]:
        """Get all tools (simple + navigation + thinking + memory + legacy + complex)."""
        tools = []
        tools.extend(ToolRegistry.get_simple_tools())
        tools.extend(ToolRegistry.get_navigation_tools())
        tools.extend(ToolRegistry.get_thinking_tools())
        tools.extend(ToolRegistry.get_memory_tools())
        tools.extend(ToolRegistry.get_legacy_tools())
        tools.extend(ToolRegistry.get_complex_tools())
        return tools