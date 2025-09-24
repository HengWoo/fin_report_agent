"""
Restaurant Financial Analysis MCP Server

Main MCP server implementation for restaurant financial analysis,
providing tools for Excel parsing, validation, and financial analysis.
"""

import logging
from typing import Optional
from pathlib import Path
import traceback
from datetime import datetime

from mcp import Tool, Resource
from mcp.server import Server
from mcp.types import AnyUrl, TextContent

from .config import MCPServerConfig
from .tools import FinancialAnalysisTools
from .validation_config import VALIDATION_TOOL_DESCRIPTIONS
from .validation_state import validation_state_manager
from ..analyzers.restaurant_analytics import RestaurantAnalyticsEngine
from ..analyzers.adaptive_financial_analyzer import AdaptiveFinancialAnalyzer
from ..parsers.chinese_excel_parser import ChineseExcelParser
from ..parsers.account_hierarchy_parser import AccountHierarchyParser
from ..validators.restaurant_validator import RestaurantFinancialValidator
from .simple_tools import (
    read_excel_region,
    search_in_excel,
    get_excel_info,
    calculate,
    show_excel_visual
)
from .financial_memory import financial_memory_manager
from .financial_navigator import financial_navigator
from .thinking_tools import thinking_tools


class RestaurantFinancialMCPServer:
    """MCP Server for Restaurant Financial Analysis."""

    def __init__(self, config: Optional[MCPServerConfig] = None):
        """Initialize the MCP server."""
        self.config = config or MCPServerConfig.from_env()
        self.server = Server(self.config.server_name)
        self.tools = FinancialAnalysisTools(self.config)

        # Initialize analysis components
        self.analytics_engine = RestaurantAnalyticsEngine()
        self.adaptive_analyzer = AdaptiveFinancialAnalyzer()
        self.parser = ChineseExcelParser()
        self.hierarchy_parser = AccountHierarchyParser()
        self.validator = RestaurantFinancialValidator()

        # Setup logging
        self._setup_logging()

        # Register handlers
        self._register_handlers()

        self.logger.info(f"MCP Server initialized: {self.config.server_name} v{self.config.server_version}")

    def _setup_logging(self) -> None:
        """Setup logging configuration for MCP server (file-only to avoid stdio conflicts)."""
        self.logger = logging.getLogger(self.config.server_name)
        self.logger.setLevel(getattr(logging, self.config.log_level.upper()))

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File handler (required to avoid stdio interference)
        log_file = self.config.log_file or "mcp_server.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, self.config.log_level.upper()))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # IMPORTANT: No console handler to avoid interfering with MCP stdio communication

    def _register_handlers(self) -> None:
        """Register MCP handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="parse_excel",
                    description=VALIDATION_TOOL_DESCRIPTIONS.get("parse_excel", "Parse Chinese restaurant Excel financial statements into structured data"),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Excel file to parse"
                            },
                            "sheet_name": {
                                "type": "string",
                                "description": "Name of the sheet to parse (optional, defaults to first sheet)"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="validate_financial_data",
                    description="Validate restaurant financial data against industry standards and business rules",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "financial_data": {
                                "type": "object",
                                "description": "Financial data to validate (income statement format)"
                            },
                            "strict_mode": {
                                "type": "boolean",
                                "description": "Enable strict validation mode (default: false)"
                            }
                        },
                        "required": ["financial_data"]
                    }
                ),
                Tool(
                    name="calculate_kpis",
                    description=VALIDATION_TOOL_DESCRIPTIONS.get("calculate_kpis", "Calculate restaurant KPIs and performance metrics from financial data"),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "income_statement": {
                                "type": "object",
                                "description": "Income statement data for KPI calculation"
                            },
                            "include_benchmarks": {
                                "type": "boolean",
                                "description": "Include industry benchmark comparisons (default: true)"
                            }
                        },
                        "required": ["income_statement"]
                    }
                ),
                Tool(
                    name="analyze_trends",
                    description="Perform trend analysis on historical restaurant financial data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "historical_statements": {
                                "type": "array",
                                "description": "Array of historical income statements",
                                "items": {"type": "object"}
                            },
                            "include_forecasting": {
                                "type": "boolean",
                                "description": "Include future trend forecasting (default: true)"
                            }
                        },
                        "required": ["historical_statements"]
                    }
                ),
                Tool(
                    name="generate_insights",
                    description="Generate business insights and recommendations from restaurant data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "kpis": {
                                "type": "object",
                                "description": "Restaurant KPIs data"
                            },
                            "income_statement": {
                                "type": "object",
                                "description": "Income statement data"
                            },
                            "language": {
                                "type": "string",
                                "description": "Output language (en/zh/both, default: both)"
                            }
                        },
                        "required": ["kpis", "income_statement"]
                    }
                ),
                Tool(
                    name="comprehensive_analysis",
                    description=VALIDATION_TOOL_DESCRIPTIONS.get("comprehensive_analysis", "Perform complete restaurant financial analysis from Excel file to insights"),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Excel file to analyze"
                            },
                            "language": {
                                "type": "string",
                                "description": "Output language (en/zh/both, default: both)"
                            },
                            "include_executive_summary": {
                                "type": "boolean",
                                "description": "Include executive summary (default: true)"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="adaptive_financial_analysis",
                    description=VALIDATION_TOOL_DESCRIPTIONS.get("adaptive_financial_analysis", "Intelligent financial analysis that adapts to any Excel format using AI agents"),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Excel file to analyze"
                            },
                            "analysis_focus": {
                                "type": "string",
                                "description": "Focus area: 'profitability', 'growth', 'efficiency', or 'comprehensive' (default: comprehensive)",
                                "enum": ["profitability", "growth", "efficiency", "comprehensive"]
                            },
                            "business_context": {
                                "type": "string",
                                "description": "Optional business context (e.g., 'new_location', 'seasonal_business', 'chain_restaurant')"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                # SIMPLE TOOLS - Claude-driven intelligence
                Tool(
                    name="read_excel_region",
                    description="Extract a rectangular region of cells from Excel. Returns raw data with no interpretation. Let Claude decide what it means.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to Excel file"},
                            "start_row": {"type": "integer", "description": "Starting row (0-indexed)"},
                            "end_row": {"type": "integer", "description": "Ending row (inclusive)"},
                            "start_col": {"type": "integer", "description": "Starting column (0-indexed)"},
                            "end_col": {"type": "integer", "description": "Ending column (inclusive)"}
                        },
                        "required": ["file_path", "start_row", "end_row", "start_col", "end_col"]
                    }
                ),
                Tool(
                    name="search_in_excel",
                    description="Find all cells containing a search term. Returns locations and values. Claude interprets what the matches mean.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to Excel file"},
                            "search_term": {"type": "string", "description": "Text to search for"},
                            "case_sensitive": {"type": "boolean", "description": "Match case (default: false)"}
                        },
                        "required": ["file_path", "search_term"]
                    }
                ),
                Tool(
                    name="get_excel_info",
                    description="Get basic Excel file structure: rows, columns, sheet names. No interpretation, just dimensions.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to Excel file"}
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="calculate",
                    description="Perform simple math: sum, average, max, min. Claude decides what to calculate, tool just does the math.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {"type": "string", "description": "One of: sum, average, max, min"},
                            "values": {"type": "array", "items": {"type": "number"}, "description": "List of numbers"}
                        },
                        "required": ["operation", "values"]
                    }
                ),
                Tool(
                    name="show_excel_visual",
                    description="Display Excel in readable format for Claude to analyze. Shows raw data with row/column labels.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to Excel file"},
                            "max_rows": {"type": "integer", "description": "Max rows to show (default: 20)"},
                            "max_cols": {"type": "integer", "description": "Max columns to show (default: 10)"}
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="validate_account_structure",
                    description="MANDATORY first step: Parse Excel and extract account hierarchy for validation. Shows parent-child relationships and asks user to confirm structure before any calculations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Excel file to analyze"
                            },
                            "show_details": {
                                "type": "boolean",
                                "description": "Show detailed account breakdown (default: true)"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                # MULTI-TURN INTELLIGENCE TOOLS
                Tool(
                    name="find_account",
                    description="Search for financial accounts by name pattern (like LSP find_symbol). Supports Chinese/English terms and hierarchical navigation.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to Excel file"},
                            "name_pattern": {"type": "string", "description": "Account name or pattern to search for"},
                            "exact_match": {"type": "boolean", "description": "Exact match only (default: false)"},
                            "account_type": {"type": "string", "description": "Filter by type: asset, liability, revenue, expense, etc."}
                        },
                        "required": ["file_path", "name_pattern"]
                    }
                ),
                Tool(
                    name="get_financial_overview",
                    description="Get high-level financial structure overview (like LSP symbols overview). Shows top-level accounts and hierarchy.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to Excel file"},
                            "max_depth": {"type": "integer", "description": "Maximum hierarchy depth to show (default: 2)"}
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="get_account_context",
                    description="Get account with surrounding context - parent, children, siblings (like reading code with context lines).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to Excel file"},
                            "account_name_path": {"type": "string", "description": "Full account name path"},
                            "depth": {"type": "integer", "description": "Context depth (default: 1)"}
                        },
                        "required": ["file_path", "account_name_path"]
                    }
                ),
                Tool(
                    name="think_about_financial_data",
                    description="Reflect on collected financial data and assess if enough information has been gathered for analysis. Returns recommendations for next steps.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collected_data": {"type": "object", "description": "Summary of data collected so far"},
                            "analysis_goal": {"type": "string", "description": "The analysis goal or objective"}
                        },
                        "required": ["collected_data", "analysis_goal"]
                    }
                ),
                Tool(
                    name="think_about_analysis_completeness",
                    description="Check if financial analysis is complete against requirements. Identifies missing components.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_performed": {"type": "array", "items": {"type": "string"}, "description": "List of completed analysis steps"},
                            "required_components": {"type": "array", "items": {"type": "string"}, "description": "List of required components"}
                        },
                        "required": ["analysis_performed", "required_components"]
                    }
                ),
                Tool(
                    name="think_about_assumptions",
                    description="Validate financial assumptions against context and best practices. Ensures assumptions are documented and reasonable.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "assumptions": {"type": "object", "description": "Assumptions made during analysis"},
                            "financial_context": {"type": "object", "description": "Financial context for validation"}
                        },
                        "required": ["assumptions", "financial_context"]
                    }
                ),
                Tool(
                    name="save_analysis_insight",
                    description="Save a discovered insight or pattern to memory for future reference. Builds knowledge across sessions.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Current session ID"},
                            "key": {"type": "string", "description": "Insight key/identifier"},
                            "description": {"type": "string", "description": "Insight description"},
                            "insight_type": {"type": "string", "description": "Type: pattern, anomaly, recommendation, etc."},
                            "context": {"type": "object", "description": "Context data"},
                            "confidence": {"type": "number", "description": "Confidence level 0.0-1.0 (default: 0.8)"}
                        },
                        "required": ["session_id", "key", "description", "insight_type", "context"]
                    }
                ),
                Tool(
                    name="get_session_context",
                    description="Get analysis session context and history. Shows what's been done in current session.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session ID"}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="write_memory_note",
                    description="Write a memory note about financial patterns or domain knowledge (like Serena's memory files).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Memory note name"},
                            "content": {"type": "string", "description": "Memory content in markdown format"},
                            "session_id": {"type": "string", "description": "Optional session ID to associate"}
                        },
                        "required": ["name", "content"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            try:
                self.logger.info(f"Tool called: {name} with arguments: {arguments}")

                # Simple tools - Claude-driven intelligence
                if name == "read_excel_region":
                    result = await self._handle_read_excel_region(arguments)
                elif name == "search_in_excel":
                    result = await self._handle_search_in_excel(arguments)
                elif name == "get_excel_info":
                    result = await self._handle_get_excel_info(arguments)
                elif name == "calculate":
                    result = await self._handle_calculate(arguments)
                elif name == "show_excel_visual":
                    result = await self._handle_show_excel_visual(arguments)
                # Complex tools - for compatibility
                elif name == "parse_excel":
                    result = await self._handle_parse_excel(arguments)
                elif name == "validate_financial_data":
                    result = await self._handle_validate_financial_data(arguments)
                elif name == "calculate_kpis":
                    result = await self._handle_calculate_kpis(arguments)
                elif name == "analyze_trends":
                    result = await self._handle_analyze_trends(arguments)
                elif name == "generate_insights":
                    result = await self._handle_generate_insights(arguments)
                elif name == "comprehensive_analysis":
                    result = await self._handle_comprehensive_analysis(arguments)
                elif name == "adaptive_financial_analysis":
                    result = await self._handle_adaptive_financial_analysis(arguments)
                elif name == "validate_account_structure":
                    result = await self._handle_validate_account_structure(arguments)
                # Multi-turn intelligence tools
                elif name == "find_account":
                    result = await self._handle_find_account(arguments)
                elif name == "get_financial_overview":
                    result = await self._handle_get_financial_overview(arguments)
                elif name == "get_account_context":
                    result = await self._handle_get_account_context(arguments)
                elif name == "think_about_financial_data":
                    result = await self._handle_think_about_financial_data(arguments)
                elif name == "think_about_analysis_completeness":
                    result = await self._handle_think_about_analysis_completeness(arguments)
                elif name == "think_about_assumptions":
                    result = await self._handle_think_about_assumptions(arguments)
                elif name == "save_analysis_insight":
                    result = await self._handle_save_analysis_insight(arguments)
                elif name == "get_session_context":
                    result = await self._handle_get_session_context(arguments)
                elif name == "write_memory_note":
                    result = await self._handle_write_memory_note(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                self.logger.info(f"Tool {name} completed successfully")
                return [result]

            except Exception as e:
                self.logger.error(f"Error in tool {name}: {str(e)}")
                self.logger.error(traceback.format_exc())
                return [TextContent(
                    type="text",
                    text=f"❌ Error in {name}: {str(e)}"
                )]

        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri=AnyUrl("file://demo_data/sample_restaurant_data.xlsx"),
                    name="Sample Restaurant Data",
                    description="Sample Chinese restaurant financial data for testing",
                    mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
                Resource(
                    uri=AnyUrl("file://docs/api_documentation.md"),
                    name="API Documentation",
                    description="Documentation for the Restaurant Financial Analysis API",
                    mimeType="text/markdown"
                )
            ]

    async def _handle_parse_excel(self, arguments: dict) -> TextContent:
        """
        Handle Excel parsing tool call.

        NEW: Now uses AccountHierarchyParser with column intelligence instead of ChineseExcelParser
        to prevent double counting and exclude non-financial columns.
        """
        file_path = arguments.get("file_path")
        sheet_name = arguments.get("sheet_name")

        if not file_path:
            raise ValueError("file_path is required")

        # Check file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # NEW: Use AccountHierarchyParser with column intelligence
        hierarchy_result = self.hierarchy_parser.parse_hierarchy(file_path)

        if hierarchy_result.get("parsing_status") == "success":
            accounts = hierarchy_result.get("accounts", [])
            column_intelligence = hierarchy_result.get("column_intelligence", {})

            # Get column intelligence summary
            value_columns = column_intelligence.get("value_columns", [])
            subtotal_columns = column_intelligence.get("subtotal_columns", [])
            excluded = column_intelligence.get("excluded_columns", {})

            # Format as readable text
            output = "📊 Excel文件解析成功 (智能列识别)\n"
            output += f"文件路径: {file_path}\n"
            output += f"发现账户: {len(accounts)} 个\n"

            # Column intelligence summary
            output += "\n🧠 列智能分析:\n"
            output += f"• 数值列: {len(value_columns)} 个\n"
            output += f"• 小计列: {len(subtotal_columns)} 个 (用于值，不参与求和)\n"

            total_excluded = sum(len(cols) for cols in excluded.values())
            if total_excluded > 0:
                output += f"• 排除列: {total_excluded} 个\n"
                if excluded.get('notes'):
                    output += f"  - 备注列: {len(excluded['notes'])} 个\n"
                if excluded.get('ratios'):
                    output += f"  - 占比列: {len(excluded['ratios'])} 个\n"
                if excluded.get('subtotals'):
                    output += f"  - 小计列: {len(excluded['subtotals'])} 个 (防止重复计算)\n"

            # Show sample accounts
            if accounts:
                output += "\n主要账户示例:\n"
                for account in accounts[:5]:
                    name = account.get('name', '')
                    value = account.get('total_value', 0)
                    used_subtotal = account.get('used_subtotal', False)
                    marker = " ✓(小计)" if used_subtotal else ""
                    output += f"• {name}: ¥{value:,.2f}{marker}\n"
                if len(accounts) > 5:
                    output += f"• ... 还有 {len(accounts) - 5} 个账户\n"

            # Show column intelligence report if available
            col_report = column_intelligence.get("classification_report", "")
            if col_report:
                output += "\n" + "="*50 + "\n"
                output += col_report

            return TextContent(type="text", text=output)
        else:
            error_msg = hierarchy_result.get("error", "Unknown parsing error")
            return TextContent(type="text", text=f"❌ 解析失败: {error_msg}")

    async def _handle_validate_financial_data(self, arguments: dict) -> TextContent:
        """Handle financial data validation tool call."""
        financial_data = arguments.get("financial_data")
        strict_mode = arguments.get("strict_mode", False)

        if not financial_data:
            raise ValueError("financial_data is required")

        # Perform validation using the validator
        try:
            validation_results = self.validator.validate_restaurant_data(financial_data)

            output = "✅ 财务数据验证完成\n"
            output += f"严格模式: {'开启' if strict_mode else '关闭'}\n"

            if validation_results.get("is_valid", True):
                output += "验证状态: ✅ 通过\n"
            else:
                output += "验证状态: ❌ 发现问题\n"

            errors = validation_results.get("errors", [])
            warnings = validation_results.get("warnings", [])

            if errors:
                output += f"\n❌ 错误 ({len(errors)} 项):\n"
                for error in errors[:3]:
                    output += f"• {error}\n"
                if len(errors) > 3:
                    output += f"• ... 还有 {len(errors) - 3} 个错误\n"

            if warnings:
                output += f"\n⚠️ 警告 ({len(warnings)} 项):\n"
                for warning in warnings[:3]:
                    output += f"• {warning}\n"
                if len(warnings) > 3:
                    output += f"• ... 还有 {len(warnings) - 3} 个警告\n"

            return TextContent(type="text", text=output)

        except Exception as e:
            return TextContent(type="text", text=f"❌ 验证失败: {str(e)}")

    async def _handle_calculate_kpis(self, arguments: dict) -> TextContent:
        """Handle KPI calculation tool call."""
        income_statement_data = arguments.get("income_statement")
        include_benchmarks = arguments.get("include_benchmarks", True)

        if not income_statement_data:
            raise ValueError("income_statement is required")

        try:
            # Use analytics engine to calculate KPIs
            kpis = self.analytics_engine.calculate_kpis(income_statement_data)

            output = "📊 餐厅关键绩效指标 (KPI) 分析\n"
            output += "=" * 40 + "\n"

            # Profitability metrics
            if "profitability" in kpis:
                profit_metrics = kpis["profitability"]
                output += "\n💰 盈利能力指标:\n"

                if "gross_margin" in profit_metrics:
                    gm = profit_metrics["gross_margin"] * 100
                    status = "✅优秀" if gm > 65 else "⚠️一般" if gm > 60 else "❌偏低"
                    output += f"• 毛利率: {gm:.1f}% {status}\n"

                if "operating_margin" in profit_metrics:
                    om = profit_metrics["operating_margin"] * 100
                    status = "✅优秀" if om > 20 else "⚠️一般" if om > 15 else "❌偏低"
                    output += f"• 营业利润率: {om:.1f}% {status}\n"

            # Efficiency metrics
            if "efficiency" in kpis:
                eff_metrics = kpis["efficiency"]
                output += "\n⚡ 运营效率指标:\n"

                if "food_cost_percentage" in eff_metrics:
                    fcp = eff_metrics["food_cost_percentage"] * 100
                    status = "✅优秀" if fcp < 30 else "⚠️一般" if fcp < 35 else "❌偏高"
                    output += f"• 食品成本率: {fcp:.1f}% {status}\n"

                if "labor_cost_percentage" in eff_metrics:
                    lcp = eff_metrics["labor_cost_percentage"] * 100
                    status = "✅优秀" if lcp < 28 else "⚠️一般" if lcp < 35 else "❌偏高"
                    output += f"• 人工成本率: {lcp:.1f}% {status}\n"

            # Industry benchmarks
            if include_benchmarks:
                output += "\n🏭 行业基准对比:\n"
                output += "• 毛利率目标: 60-70%\n"
                output += "• 食品成本率: 28-35%\n"
                output += "• 人工成本率: 25-35%\n"
                output += "• 主成本率: <60%\n"

            return TextContent(type="text", text=output)

        except Exception as e:
            return TextContent(type="text", text=f"❌ KPI计算失败: {str(e)}")

    async def _handle_analyze_trends(self, arguments: dict) -> TextContent:
        """Handle trend analysis tool call."""
        historical_statements = arguments.get("historical_statements")
        include_forecasting = arguments.get("include_forecasting", True)

        if not historical_statements:
            raise ValueError("historical_statements is required")

        if len(historical_statements) < 2:
            raise ValueError("At least 2 historical statements required for trend analysis")

        try:
            # Use analytics engine to perform trend analysis
            trends = self.analytics_engine.analyze_trends(historical_statements)

            output = "📈 趋势分析报告\n"
            output += "=" * 30 + "\n"
            output += f"分析期间: {len(historical_statements)} 个时间段\n"
            output += f"预测功能: {'开启' if include_forecasting else '关闭'}\n\n"

            # Revenue trends
            if "revenue_trend" in trends:
                revenue_trend = trends["revenue_trend"]
                growth_rate = revenue_trend.get("growth_rate", 0) * 100
                direction = "📈 上升" if growth_rate > 5 else "📉 下降" if growth_rate < -5 else "➡️ 稳定"
                output += f"营业收入趋势: {direction} ({growth_rate:+.1f}%)\n"

            # Cost trends
            if "cost_trends" in trends:
                cost_trends = trends["cost_trends"]
                output += "\n💸 成本趋势:\n"
                for cost_type, trend_data in cost_trends.items():
                    if isinstance(trend_data, dict) and "growth_rate" in trend_data:
                        rate = trend_data["growth_rate"] * 100
                        output += f"• {cost_type}: {rate:+.1f}%\n"

            # Forecasting
            if include_forecasting and "forecast" in trends:
                forecast = trends["forecast"]
                output += "\n🔮 预测分析:\n"
                output += f"• 下期收入预测: {forecast.get('next_period_revenue', 'N/A')}\n"
                output += f"• 增长预期: {forecast.get('growth_expectation', 'N/A')}\n"

            return TextContent(type="text", text=output)

        except Exception as e:
            return TextContent(type="text", text=f"❌ 趋势分析失败: {str(e)}")

    async def _handle_generate_insights(self, arguments: dict) -> TextContent:
        """Handle insights generation tool call."""
        kpis = arguments.get("kpis")
        income_statement = arguments.get("income_statement")
        language = arguments.get("language", "both")

        if not kpis:
            raise ValueError("kpis is required")
        if not income_statement:
            raise ValueError("income_statement is required")

        try:
            # Generate insights using the analytics engine
            insights = self.analytics_engine.generate_insights(kpis, income_statement)

            output = "💡 经营洞察与建议\n"
            output += "=" * 35 + "\n"

            # Strengths
            strengths = insights.get("strengths", [])
            if strengths:
                output += "\n✅ 经营优势:\n"
                for i, strength in enumerate(strengths[:5], 1):
                    output += f"{i}. {strength}\n"

            # Areas for improvement
            improvements = insights.get("areas_for_improvement", [])
            if improvements:
                output += "\n⚠️ 改进领域:\n"
                for i, improvement in enumerate(improvements[:5], 1):
                    output += f"{i}. {improvement}\n"

            # Recommendations
            recommendations = insights.get("recommendations", [])
            if recommendations:
                output += "\n🎯 具体建议:\n"
                for i, rec in enumerate(recommendations[:5], 1):
                    output += f"{i}. {rec}\n"

            # Add bilingual note if requested
            if language == "both" and self.config.enable_bilingual_output:
                output += "\n[双语分析完成 / Bilingual analysis completed]\n"

            return TextContent(type="text", text=output)

        except Exception as e:
            return TextContent(type="text", text=f"❌ 洞察生成失败: {str(e)}")

    async def _handle_comprehensive_analysis(self, arguments: dict) -> TextContent:
        """
        Handle comprehensive analysis using Claude Orchestrator.

        This leverages Claude's intelligence through the orchestration layer
        to perform sophisticated financial analysis without hardcoded rules.
        """
        file_path = arguments.get("file_path")
        language = arguments.get("language", "both")
        include_executive_summary = arguments.get("include_executive_summary", True)

        if not file_path:
            raise ValueError("file_path is required")

        # Check file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Use Claude Orchestrator for analysis
            self.logger.info(f"Starting orchestrated analysis of {file_path}")

            # Create orchestrator with validation manager integration
            orchestrator = ClaudeOrchestrator(
                claude_interface=MCPClaudeInterface(),
                prompts_dir="prompts/",
                validation_manager=validation_state_manager  # NEW: Pass validation manager
            )

            # Run analysis - this returns structured results OR validation requirement
            analysis_result = orchestrator.analyze_financial_report(file_path)

            # NEW: Check if validation is required first
            if analysis_result.get("validation_required"):
                output = "⚠️ 验证要求 - 必须先完成账户结构验证\n"
                output += "=" * 50 + "\n"
                output += f"📁 文件: {file_path}\n"
                output += f"状态: {analysis_result.get('status', 'validation_required')}\n\n"

                output += f"💡 {analysis_result.get('message', 'Account structure validation required')}\n\n"

                if analysis_result.get("hierarchy"):
                    hierarchy = analysis_result["hierarchy"]
                    output += "📊 发现账户结构:\n"
                    output += f"• 总账户数: {analysis_result.get('total_accounts', 0)}\n"
                    output += f"• 安全计算账户: {analysis_result.get('safe_accounts_count', 0)}\n"
                    output += f"• 潜在重复计算风险: {analysis_result.get('potential_issues', 0)}\n\n"

                output += "🔧 下一步操作:\n"
                for step in analysis_result.get("next_steps", []):
                    output += f"   {step}\n"

                output += "\n⚡ 请运行 validate_account_structure 工具完成验证！"

                return TextContent(type="text", text=output)

            # Check for analysis errors
            if analysis_result.get("error"):
                return TextContent(type="text", text=f"❌ 分析失败: {analysis_result['error']}")

            # Extract results from orchestrator
            report_type = analysis_result.get("report_type", "Unknown")
            periods = analysis_result.get("periods", [])
            calculations = analysis_result.get("calculations", {})
            validation = analysis_result.get("validation", {})
            warnings = analysis_result.get("warnings", [])

            # Build comprehensive analysis output using orchestrator results
            output = "🏪 餐厅财务综合分析报告 (Claude Orchestrated)\n"
            output += "=" * 50 + "\n"
            output += f"📁 文件: {file_path}\n"
            output += f"📈 报表类型: {report_type}\n"
            output += f"📅 分析期间: {', '.join(periods)}\n"
            output += f"🕐 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            if include_executive_summary:
                output += "📋 执行摘要\n"
                output += "-" * 30 + "\n"

                # Extract key metrics from calculations
                revenue = 0
                for key in calculations.keys():
                    if '营业收入' in key and not key.endswith('_ratio'):
                        revenue = calculations[key]
                        break

                food_cost = calculations.get('（二）.食品成本', 0)
                labor_cost = calculations.get('（三）.人工成本', 0)
                investment = calculations.get('九、长期待摊费用_total_investment', 0)

                if revenue > 0:
                    output += f"• 总营业收入: ¥{revenue:,.2f}\n"
                    output += f"• 分析期数: {len(periods)} 个期间\n"
                    output += f"• 月均收入: ¥{revenue / len(periods):,.2f}\n"

                    if food_cost > 0:
                        food_cost_ratio = (food_cost / revenue) * 100
                        output += f"• 食品成本率: {food_cost_ratio:.1f}%\n"

                    if labor_cost > 0:
                        labor_cost_ratio = (labor_cost / revenue) * 100
                        output += f"• 人工成本率: {labor_cost_ratio:.1f}%\n"

                    if investment > 0:
                        output += f"• 投资总额: ¥{investment:,.2f}\n"
                        output += f"• 投资回收期: {investment / (revenue / len(periods)):.1f} 个月\n"

                    output += "\n"

            # Show key calculations
            output += "💰 关键财务指标\n"
            output += "-" * 30 + "\n"

            # Display top calculations
            for key, value in list(calculations.items())[:10]:
                if not key.endswith('_ratio') and not key.endswith('_monthly'):
                    output += f"• {key}: ¥{value:,.2f}\n"

            # Show ratios separately
            output += "\n📊 财务比率\n"
            output += "-" * 30 + "\n"
            for key, value in calculations.items():
                if key.endswith('_ratio'):
                    output += f"• {key}: {value:.1f}%\n"

            # Validation Results
            output += "\n✅ 数据验证结果\n"
            output += "-" * 30 + "\n"
            if validation.get('valid'):
                output += "• 验证状态: ✅ 通过\n"
                output += f"• 置信度: {validation.get('confidence', 0):.1%}\n"
            else:
                output += "• 验证状态: ⚠️ 需要审查\n"
                if validation.get('issues'):
                    output += "• 发现的问题:\n"
                    for issue in validation['issues']:
                        output += f"  - {issue}\n"

            # Warnings and Suggestions
            if warnings:
                output += "\n⚠️ 注意事项\n"
                output += "-" * 30 + "\n"
                for warning in warnings:
                    output += f"• {warning}\n"

            # Analysis Phases Completed
            phases = analysis_result.get('analysis_phases', [])
            if phases:
                output += "\n🔍 分析流程\n"
                output += "-" * 30 + "\n"
                output += f"完成的分析阶段: {' → '.join(phases)}\n"

            # Language handling
            if language == "zh":
                # Already in Chinese
                pass
            elif language == "both":
                output += "\n" + "=" * 50 + "\n"
                output += "🏪 Restaurant Financial Analysis Report (Claude Orchestrated)\n"
                output += f"📁 File: {file_path}\n"
                output += f"📅 Report Type: {report_type}\n"
                output += f"📊 Analysis Periods: {', '.join(periods)}\n"
                output += "🤖 Powered by Claude Intelligence (No Hardcoded Rules)\n"
                output += "\n💡 Key Achievement: All analysis driven by Claude's understanding of financial data.\n"

            return TextContent(type="text", text=output)

        except Exception as e:
            self.logger.error(f"Orchestrated analysis failed: {str(e)}")
            return TextContent(type="text", text=f"❌ 综合分析失败: {str(e)}")

    def _get_period_column(self, period: str, periods: list) -> Optional[str]:
        """Get the column name for a specific period."""
        try:
            if period in periods:
                index = periods.index(period)
                return f"Unnamed: {index + 1}" if index > 0 else periods[0]
        except (ValueError, IndexError):
            pass
        return None

    async def _handle_adaptive_financial_analysis(self, arguments: dict) -> TextContent:
        """Handle adaptive financial analysis using AI agents."""
        file_path = arguments.get("file_path")
        analysis_focus = arguments.get("analysis_focus", "comprehensive")
        business_context = arguments.get("business_context")

        if not file_path:
            raise ValueError("file_path is required")

        # Check file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Use the adaptive analyzer to prepare analysis
            analysis_prep = await self.adaptive_analyzer.analyze_excel(
                file_path, analysis_focus, business_context
            )

            if analysis_prep["status"] == "error":
                return TextContent(type="text", text=f"❌ 分析准备失败: {analysis_prep['error']}")

            # For now, we'll create a comprehensive response using the Task agent
            # This is where the magic happens - we use Claude Code's Task tool
            output = f"🤖 智能财务分析 - {Path(file_path).name}\n"
            output += "=" * 60 + "\n"
            output += f"📊 分析重点: {analysis_focus}\n"
            if business_context:
                output += f"🏢 业务背景: {business_context}\n"
            output += f"📁 文件信息: {analysis_prep['file_info']}\n\n"

            output += "🎯 接下来将使用 Claude Code 智能代理进行深度分析...\n"
            output += "该分析将自动适应您的 Excel 格式，无需预定义的模板或映射。\n\n"

            # Include the analysis prompt for transparency
            output += "📋 分析提示:\n"
            output += "-" * 30 + "\n"
            output += analysis_prep["analysis_prompt"][:500] + "...\n\n"

            output += "✅ 准备就绪 - 请使用 Claude Code 的 Task 工具完成实际分析\n"

            return TextContent(type="text", text=output)

        except Exception as e:
            self.logger.error(f"Adaptive analysis failed: {str(e)}")
            return TextContent(type="text", text=f"❌ 智能分析失败: {str(e)}")

    async def _handle_validate_account_structure(self, arguments: dict) -> TextContent:
        """Handle account structure validation tool call."""
        try:
            file_path = arguments.get("file_path")
            show_details = arguments.get("show_details", True)

            if not file_path:
                raise ValueError("file_path is required")

            # Check file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            self.logger.info(f"Validating account structure for: {file_path}")

            # Parse account hierarchy
            hierarchy_result = self.hierarchy_parser.parse_hierarchy(file_path)

            if hierarchy_result.get("parsing_status") != "success":
                error_msg = hierarchy_result.get("error", "Unknown parsing error")
                return TextContent(type="text", text=f"❌ Account structure parsing failed: {error_msg}")

            # Format result for display
            if show_details:
                output = self.hierarchy_parser.format_hierarchy_display(hierarchy_result)
            else:
                # Brief summary
                safe_accounts = hierarchy_result["safe_accounts"]
                total_accounts = hierarchy_result["total_accounts"]
                validation = hierarchy_result["validation_flags"]

                output = "📊 Account Structure Summary\n"
                output += f"Total accounts: {total_accounts}\n"
                output += f"Safe for calculations: {len(safe_accounts)}\n"
                output += f"Potential double counting risks: {len(validation.get('potential_double_counting', []))}\n\n"

                output += "❓ Quick validation questions:\n"
                output += "1. What depreciation period applies? (typical: 3-5 years)\n"
                output += "2. Use only leaf accounts to avoid double counting?\n"

            # Add validation context
            output += "\n\n🔒 VALIDATION CHECKPOINT\n"
            output += "=" * 40 + "\n"
            output += "Before proceeding with any calculations:\n"
            output += "✅ Confirm account structure is correct\n"
            output += "✅ Specify depreciation/amortization periods\n"
            output += "✅ Choose which accounts to use for calculations\n"
            output += "✅ Document all assumptions for audit trail\n\n"

            output += "💡 TIP: Only proceed with financial analysis after user confirms all assumptions!\n"

            self.logger.info(f"Account structure validation completed for {file_path}")
            return TextContent(type="text", text=output)

        except Exception as e:
            self.logger.error(f"Account structure validation failed: {str(e)}")
            return TextContent(type="text", text=f"❌ Account structure validation failed: {str(e)}")

    # SIMPLE TOOL HANDLERS - Claude-driven intelligence
    async def _handle_read_excel_region(self, arguments: dict) -> TextContent:
        """Handle read_excel_region tool call."""
        file_path = arguments.get("file_path")
        start_row = arguments.get("start_row")
        end_row = arguments.get("end_row")
        start_col = arguments.get("start_col")
        end_col = arguments.get("end_col")

        try:
            result = read_excel_region(file_path, start_row, end_row, start_col, end_col)
            # Format as readable text
            output = "📊 Excel Region Data\n"
            output += f"Rows {start_row}-{end_row}, Columns {start_col}-{end_col}\n"
            output += "-" * 40 + "\n"
            for i, row in enumerate(result, start=start_row):
                output += f"Row {i}: {row}\n"
            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_search_in_excel(self, arguments: dict) -> TextContent:
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
            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_get_excel_info(self, arguments: dict) -> TextContent:
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
            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_calculate(self, arguments: dict) -> TextContent:
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
            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_show_excel_visual(self, arguments: dict) -> TextContent:
        """Handle show_excel_visual tool call."""
        file_path = arguments.get("file_path")
        max_rows = arguments.get("max_rows", 20)
        max_cols = arguments.get("max_cols", 10)

        try:
            visual = show_excel_visual(file_path, max_rows, max_cols)
            return TextContent(type="text", text=visual)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    # MULTI-TURN INTELLIGENCE TOOL HANDLERS
    async def _handle_find_account(self, arguments: dict) -> TextContent:
        """Handle find_account tool call."""
        file_path = arguments.get("file_path")
        name_pattern = arguments.get("name_pattern")
        exact_match = arguments.get("exact_match", False)
        account_type = arguments.get("account_type")

        try:
            accounts = financial_navigator.find_account(
                file_path, name_pattern, exact_match, account_type
            )

            output = f"🔍 Found {len(accounts)} account(s) matching '{name_pattern}'\n"
            output += "=" * 50 + "\n\n"

            for account in accounts[:10]:  # Limit to 10
                output += f"📌 {account.name}\n"
                output += f"   Path: {account.name_path}\n"
                output += f"   Type: {account.account_type}\n"
                output += f"   Level: {account.level}\n"
                if account.values:
                    output += f"   Values: {account.values}\n"
                output += f"   {'🍃 Leaf' if account.is_leaf() else '📂 Has children'}\n\n"

            if len(accounts) > 10:
                output += f"... and {len(accounts) - 10} more accounts\n"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_get_financial_overview(self, arguments: dict) -> TextContent:
        """Handle get_financial_overview tool call."""
        file_path = arguments.get("file_path")
        max_depth = arguments.get("max_depth", 2)

        try:
            overview = financial_navigator.get_financial_overview(file_path, max_depth)

            output = f"📊 Financial Structure Overview (depth ≤ {max_depth})\n"
            output += "=" * 50 + "\n\n"

            current_level = -1
            for account in overview:
                if account.level != current_level:
                    current_level = account.level
                    output += f"\n{'━' * 40}\n"
                    output += f"Level {current_level}\n"
                    output += f"{'━' * 40}\n\n"

                indent = "  " * account.level
                icon = "🍃" if account.is_leaf() else "📂"
                output += f"{indent}{icon} {account.name} ({account.account_type})\n"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_get_account_context(self, arguments: dict) -> TextContent:
        """Handle get_account_context tool call."""
        file_path = arguments.get("file_path")
        account_name_path = arguments.get("account_name_path")
        depth = arguments.get("depth", 1)

        try:
            context = financial_navigator.get_account_context(
                file_path, account_name_path, depth
            )

            if "error" in context:
                return TextContent(type="text", text=f"❌ {context['error']}")

            account = context["account"]
            output = f"📍 Account Context: {account['name']}\n"
            output += "=" * 50 + "\n\n"

            output += "**Account Details:**\n"
            output += f"  Path: {account['name_path']}\n"
            output += f"  Type: {account['account_type']}\n"
            output += f"  Level: {account['level']}\n"
            output += f"  Status: {'🍃 Leaf' if account['is_leaf'] else '📂 Parent'}\n\n"

            if context.get("ancestors"):
                output += "**Ancestors (path from root):**\n"
                for anc in reversed(context["ancestors"]):
                    output += f"  └─ {anc['name']}\n"
                output += "\n"

            if context.get("children"):
                output += f"**Children ({len(context['children'])}):**\n"
                for child in context["children"][:5]:
                    output += f"  ├─ {child['name']} ({child['account_type']})\n"
                if len(context["children"]) > 5:
                    output += f"  └─ ... and {len(context['children']) - 5} more\n"
                output += "\n"

            if context.get("siblings"):
                output += f"**Siblings ({len(context['siblings'])}):**\n"
                for sib in context["siblings"][:3]:
                    output += f"  • {sib['name']}\n"
                if len(context["siblings"]) > 3:
                    output += f"  • ... and {len(context['siblings']) - 3} more\n"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_think_about_financial_data(self, arguments: dict) -> TextContent:
        """Handle think_about_financial_data tool call."""
        collected_data = arguments.get("collected_data", {})
        analysis_goal = arguments.get("analysis_goal", "")

        try:
            result = thinking_tools.think_about_financial_data(collected_data, analysis_goal)

            output = "🤔 Reflection: Financial Data Assessment\n"
            output += "=" * 50 + "\n\n"
            output += f"**Summary:** {result.summary}\n"
            output += f"**Confidence:** {result.confidence * 100:.0f}%\n\n"

            output += f"**Analysis Goal:** {analysis_goal}\n\n"

            if result.recommendations:
                output += "**Recommendations:**\n"
                for rec in result.recommendations:
                    output += f"  {rec}\n"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_think_about_analysis_completeness(self, arguments: dict) -> TextContent:
        """Handle think_about_analysis_completeness tool call."""
        analysis_performed = arguments.get("analysis_performed", [])
        required_components = arguments.get("required_components", [])

        try:
            result = thinking_tools.think_about_analysis_completeness(
                analysis_performed, required_components
            )

            output = "✅ Analysis Completeness Check\n"
            output += "=" * 50 + "\n\n"
            output += f"**Summary:** {result.summary}\n"
            output += f"**Completion Rate:** {result.confidence * 100:.0f}%\n\n"

            details = result.details
            output += f"**Completed:** {details['completed_count']}/{details['total_required']}\n"

            if details.get("completed"):
                output += "\n**✅ Completed Components:**\n"
                for comp in details["completed"]:
                    output += f"  ✓ {comp}\n"

            if details.get("missing"):
                output += "\n**❌ Missing Components:**\n"
                for comp in details["missing"]:
                    output += f"  ✗ {comp}\n"

            if result.recommendations:
                output += "\n**Next Steps:**\n"
                for rec in result.recommendations:
                    output += f"  {rec}\n"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_think_about_assumptions(self, arguments: dict) -> TextContent:
        """Handle think_about_assumptions tool call."""
        assumptions = arguments.get("assumptions", {})
        financial_context = arguments.get("financial_context", {})

        try:
            result = thinking_tools.think_about_assumptions(assumptions, financial_context)

            output = "🔍 Assumption Validation\n"
            output += "=" * 50 + "\n\n"
            output += f"**Summary:** {result.summary}\n"
            output += f"**Validation Score:** {result.confidence * 100:.0f}%\n\n"

            validation_results = result.details.get("validation_results", [])
            if validation_results:
                output += "**Validation Results:**\n"
                for val in validation_results:
                    icon = "✅" if val["valid"] else "⚠️"
                    output += f"  {icon} {val.get('reason', 'N/A')}\n"

            if result.recommendations:
                output += "\n**Recommendations:**\n"
                for rec in result.recommendations:
                    output += f"  {rec}\n"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_save_analysis_insight(self, arguments: dict) -> TextContent:
        """Handle save_analysis_insight tool call."""
        session_id = arguments.get("session_id")
        key = arguments.get("key")
        description = arguments.get("description")
        insight_type = arguments.get("insight_type")
        context = arguments.get("context", {})
        confidence = arguments.get("confidence", 0.8)

        try:
            success = financial_memory_manager.save_insight(
                session_id, key, description, insight_type, context, confidence
            )

            if success:
                output = "💾 Insight Saved Successfully\n"
                output += "=" * 50 + "\n\n"
                output += f"**Key:** {key}\n"
                output += f"**Type:** {insight_type}\n"
                output += f"**Description:** {description}\n"
                output += f"**Confidence:** {confidence * 100:.0f}%\n"
                output += f"**Session:** {session_id}\n"
            else:
                output = f"❌ Failed to save insight (session not found: {session_id})"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_get_session_context(self, arguments: dict) -> TextContent:
        """Handle get_session_context tool call."""
        session_id = arguments.get("session_id")

        try:
            context = financial_memory_manager.get_context_summary(session_id)

            if "error" in context:
                return TextContent(type="text", text=f"❌ {context['error']}")

            output = "📋 Session Context Summary\n"
            output += "=" * 50 + "\n\n"
            output += f"**Session ID:** {context['session_id']}\n"
            output += f"**File:** {context['file_path']}\n"
            output += f"**Created:** {context['created_at']}\n"
            output += f"**Last Accessed:** {context['last_accessed']}\n\n"

            output += "**Statistics:**\n"
            output += f"  • Insights: {context['insights_count']}\n"
            output += f"  • Patterns: {context['patterns_count']}\n"
            output += f"  • History Events: {context['history_count']}\n"
            output += f"  • Questions Asked: {context['questions_asked_count']}\n\n"

            if context.get("recent_insights"):
                output += "**Recent Insights:**\n"
                for insight in context["recent_insights"]:
                    output += f"  • [{insight['insight_type']}] {insight['description']}\n"

            if context.get("user_preferences"):
                output += f"\n**User Preferences:** {len(context['user_preferences'])} set\n"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    async def _handle_write_memory_note(self, arguments: dict) -> TextContent:
        """Handle write_memory_note tool call."""
        name = arguments.get("name")
        content = arguments.get("content")
        session_id = arguments.get("session_id")

        try:
            success = financial_memory_manager.write_memory_file(name, content, session_id)

            if success:
                output = "📝 Memory Note Saved\n"
                output += "=" * 50 + "\n\n"
                output += f"**Name:** {name}.md\n"
                if session_id:
                    output += f"**Session:** {session_id}\n"
                output += "\n**Content Preview:**\n"
                output += content[:200] + ("..." if len(content) > 200 else "")
            else:
                output = "❌ Failed to save memory note"

            return TextContent(type="text", text=output)
        except Exception as e:
            return TextContent(type="text", text=f"❌ Error: {str(e)}")

    def get_server(self) -> Server:
        """Get the underlying MCP server instance."""
        return self.server