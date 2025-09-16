"""
Restaurant Financial Analysis MCP Server

Main MCP server implementation for restaurant financial analysis,
providing tools for Excel parsing, validation, and financial analysis.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Sequence
from pathlib import Path
import traceback

from mcp import Tool, Resource
from mcp.server import Server
from mcp.types import AnyUrl
from pydantic import BaseModel

from .config import MCPServerConfig, DEFAULT_TOOL_CONFIGS
from .tools import FinancialAnalysisTools
from ..analyzers.restaurant_analytics import RestaurantAnalyticsEngine
from ..parsers.chinese_excel_parser import ChineseExcelParser
from ..validators.restaurant_validator import RestaurantFinancialValidator


class RestaurantFinancialMCPServer:
    """MCP Server for Restaurant Financial Analysis."""

    def __init__(self, config: Optional[MCPServerConfig] = None):
        """Initialize the MCP server."""
        self.config = config or MCPServerConfig.from_env()
        self.server = Server(self.config.server_name)
        self.tools = FinancialAnalysisTools(self.config)

        # Initialize analysis components
        self.analytics_engine = RestaurantAnalyticsEngine()
        self.parser = ChineseExcelParser()
        self.validator = RestaurantFinancialValidator()

        # Setup logging
        self._setup_logging()

        # Register handlers
        self._register_handlers()

        self.logger.info(f"MCP Server initialized: {self.config.server_name} v{self.config.server_version}")

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger(self.config.server_name)
        self.logger.setLevel(getattr(logging, self.config.log_level.upper()))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.log_level.upper()))

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler if specified
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(getattr(logging, self.config.log_level.upper()))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _register_handlers(self) -> None:
        """Register MCP handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="parse_excel",
                    description="Parse Chinese restaurant Excel financial statements into structured data",
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
                    description="Calculate restaurant KPIs and performance metrics from financial data",
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
                    description="Perform complete restaurant financial analysis from Excel file to insights",
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
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[object]:
            """Handle tool calls."""
            try:
                self.logger.info(f"Tool called: {name} with arguments: {arguments}")

                if name == "parse_excel":
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
                else:
                    raise ValueError(f"Unknown tool: {name}")

                self.logger.info(f"Tool {name} completed successfully")
                return [result]

            except Exception as e:
                self.logger.error(f"Error in tool {name}: {str(e)}")
                self.logger.error(traceback.format_exc())
                return [{
                    "error": str(e),
                    "type": type(e).__name__,
                    "tool": name
                }]

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

    async def _handle_parse_excel(self, arguments: dict) -> dict:
        """Handle Excel parsing tool call."""
        file_path = arguments.get("file_path")
        sheet_name = arguments.get("sheet_name")

        if not file_path:
            raise ValueError("file_path is required")

        # Check file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Parse Excel file
        result = self.parser.parse_income_statement(file_path, sheet_name)

        return {
            "success": True,
            "file_path": file_path,
            "sheet_name": sheet_name,
            "periods": result.get("periods", []),
            "financial_data": result.get("financial_data", {}),
            "metadata": {
                "parser_version": "1.0.0",
                "parsed_at": str(asyncio.get_event_loop().time())
            }
        }

    async def _handle_validate_financial_data(self, arguments: dict) -> dict:
        """Handle financial data validation tool call."""
        financial_data = arguments.get("financial_data")
        strict_mode = arguments.get("strict_mode", False)

        if not financial_data:
            raise ValueError("financial_data is required")

        # Convert to income statement and validate
        # This would need to be implemented based on the financial_data structure
        validation_results = []  # Placeholder for validation logic

        return {
            "success": True,
            "validation_results": validation_results,
            "strict_mode": strict_mode,
            "is_valid": len(validation_results) == 0
        }

    async def _handle_calculate_kpis(self, arguments: dict) -> dict:
        """Handle KPI calculation tool call."""
        income_statement_data = arguments.get("income_statement")
        include_benchmarks = arguments.get("include_benchmarks", True)

        if not income_statement_data:
            raise ValueError("income_statement is required")

        # This would need income statement conversion logic
        # For now, return placeholder structure
        return {
            "success": True,
            "kpis": {
                "profitability": {},
                "efficiency": {},
                "growth": {},
                "liquidity": {},
                "risk": {}
            },
            "benchmarks_included": include_benchmarks
        }

    async def _handle_analyze_trends(self, arguments: dict) -> dict:
        """Handle trend analysis tool call."""
        historical_statements = arguments.get("historical_statements")
        include_forecasting = arguments.get("include_forecasting", True)

        if not historical_statements:
            raise ValueError("historical_statements is required")

        if len(historical_statements) < 2:
            raise ValueError("At least 2 historical statements required for trend analysis")

        return {
            "success": True,
            "trends": {
                "growth_rates": {},
                "trend_direction": "stable",
                "forecasting_included": include_forecasting
            }
        }

    async def _handle_generate_insights(self, arguments: dict) -> dict:
        """Handle insights generation tool call."""
        kpis = arguments.get("kpis")
        income_statement = arguments.get("income_statement")
        language = arguments.get("language", "both")

        if not kpis:
            raise ValueError("kpis is required")
        if not income_statement:
            raise ValueError("income_statement is required")

        return {
            "success": True,
            "insights": {
                "strengths": [],
                "areas_for_improvement": [],
                "recommendations": []
            },
            "language": language,
            "bilingual_output": self.config.enable_bilingual_output
        }

    async def _handle_comprehensive_analysis(self, arguments: dict) -> dict:
        """Handle comprehensive analysis tool call."""
        file_path = arguments.get("file_path")
        language = arguments.get("language", "both")
        include_executive_summary = arguments.get("include_executive_summary", True)

        if not file_path:
            raise ValueError("file_path is required")

        # Check file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Use the analytics engine for comprehensive analysis
            result = self.analytics_engine.analyze_restaurant_excel(file_path)

            # Convert result to dictionary if it's an object
            if hasattr(result, 'to_dict'):
                analysis_data = result.to_dict()
            else:
                analysis_data = result

            return {
                "success": True,
                "file_path": file_path,
                "analysis": analysis_data,
                "language": language,
                "executive_summary_included": include_executive_summary,
                "generated_at": str(asyncio.get_event_loop().time())
            }

        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {str(e)}")
            raise

    async def start(self) -> None:
        """Start the MCP server."""
        self.logger.info(f"Starting MCP server on {self.config.host}:{self.config.port}")

        # For MCP, we typically run the server using the MCP transport
        # This is a placeholder for the actual server startup logic
        self.logger.info("MCP server ready to handle requests")

    async def stop(self) -> None:
        """Stop the MCP server."""
        self.logger.info("Stopping MCP server")

    def get_server(self) -> Server:
        """Get the underlying MCP server instance."""
        return self.server