"""
MCP Server Configuration

Configuration settings for the Restaurant Financial Analysis MCP Server.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from pathlib import Path


class MCPServerConfig(BaseModel):
    """Configuration for the MCP Server."""

    # Server settings
    server_name: str = "restaurant-financial-analysis"
    server_version: str = "1.0.0"
    description: str = "MCP Server for Restaurant Financial Analysis"

    # Host and port settings
    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # File handling
    max_file_size_mb: int = Field(default=50, description="Maximum Excel file size in MB")
    allowed_file_extensions: List[str] = Field(
        default=[".xlsx", ".xls"],
        description="Allowed Excel file extensions"
    )

    # Analysis settings
    default_language: str = Field(default="en", description="Default output language (en/zh)")
    enable_bilingual_output: bool = Field(default=True, description="Enable bilingual output")

    # Performance settings
    max_concurrent_analyses: int = Field(default=5, description="Maximum concurrent analyses")
    analysis_timeout_seconds: int = Field(default=300, description="Analysis timeout in seconds")

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")

    # Cache settings
    enable_cache: bool = Field(default=True, description="Enable result caching")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")

    # Security settings
    require_auth: bool = Field(default=False, description="Require authentication")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")

    # Claude Code integration
    claude_code_enabled: bool = Field(default=True, description="Enable Claude Code integration")
    claude_code_endpoint: Optional[str] = Field(default=None, description="Claude Code endpoint")

    @classmethod
    def from_env(cls) -> "MCPServerConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("MCP_HOST", "localhost"),
            port=int(os.getenv("MCP_PORT", "8000")),
            max_file_size_mb=int(os.getenv("MCP_MAX_FILE_SIZE_MB", "50")),
            default_language=os.getenv("MCP_DEFAULT_LANGUAGE", "en"),
            enable_bilingual_output=os.getenv("MCP_BILINGUAL_OUTPUT", "true").lower() == "true",
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
            log_file=os.getenv("MCP_LOG_FILE"),
            require_auth=os.getenv("MCP_REQUIRE_AUTH", "false").lower() == "true",
            api_key=os.getenv("MCP_API_KEY"),
            claude_code_enabled=os.getenv("MCP_CLAUDE_CODE_ENABLED", "true").lower() == "true",
            claude_code_endpoint=os.getenv("MCP_CLAUDE_CODE_ENDPOINT")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()


class ToolConfig(BaseModel):
    """Configuration for individual MCP tools."""

    name: str
    description: str
    enabled: bool = True
    timeout_seconds: int = 60
    max_retries: int = 3
    cache_enabled: bool = True

    # Tool-specific settings
    settings: Dict[str, Any] = Field(default_factory=dict)


# Default tool configurations
DEFAULT_TOOL_CONFIGS = {
    "parse_excel": ToolConfig(
        name="parse_excel",
        description="Parse Chinese restaurant Excel financial statements",
        timeout_seconds=120,
        settings={
            "max_sheets": 10,
            "max_rows_per_sheet": 10000
        }
    ),
    "validate_financial_data": ToolConfig(
        name="validate_financial_data",
        description="Validate restaurant financial data against industry standards",
        timeout_seconds=30,
        settings={
            "strict_validation": False,
            "include_warnings": True
        }
    ),
    "calculate_kpis": ToolConfig(
        name="calculate_kpis",
        description="Calculate restaurant KPIs and performance metrics",
        timeout_seconds=60,
        settings={
            "include_all_categories": True,
            "benchmark_comparison": True
        }
    ),
    "analyze_trends": ToolConfig(
        name="analyze_trends",
        description="Perform trend analysis on historical financial data",
        timeout_seconds=90,
        settings={
            "min_periods": 2,
            "include_forecasting": True
        }
    ),
    "generate_insights": ToolConfig(
        name="generate_insights",
        description="Generate business insights and recommendations",
        timeout_seconds=120,
        settings={
            "max_insights_per_category": 5,
            "include_action_plans": True
        }
    ),
    "comprehensive_analysis": ToolConfig(
        name="comprehensive_analysis",
        description="Perform complete restaurant financial analysis",
        timeout_seconds=300,
        settings={
            "include_all_components": True,
            "generate_executive_summary": True
        }
    )
}