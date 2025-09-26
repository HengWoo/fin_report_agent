"""
MCP Server for Restaurant Financial Analysis

This module provides the Model Context Protocol (MCP) server implementation
for the restaurant financial analysis system, enabling integration with
Claude Code and other AI systems.
"""

from .server import FinancialAnalysisMCPServer
from .tools import FinancialAnalysisTools
from .config import MCPServerConfig

__all__ = ["FinancialAnalysisMCPServer", "FinancialAnalysisTools", "MCPServerConfig"]

__version__ = "1.0.0"
