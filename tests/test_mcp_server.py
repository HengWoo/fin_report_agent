"""
End-to-End Tests for Restaurant Financial Analysis MCP Server

Comprehensive test suite covering all aspects of the MCP server,
including tools, integration, error handling, and bilingual features.
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import date, datetime

from src.mcp_server.server import RestaurantFinancialMCPServer
from src.mcp_server.config import MCPServerConfig
from src.mcp_server.claude_integration import ClaudeCodeIntegration
from src.mcp_server.bilingual_reporter import BilingualReportGenerator, ReportLanguage, ReportFormat
from src.mcp_server.error_handling import ErrorRecoveryManager, ErrorContext, ErrorCategory, MCPError


class TestMCPServerConfig:
    """Test MCP server configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MCPServerConfig()

        assert config.server_name == "restaurant-financial-analysis"
        assert config.server_version == "1.0.0"
        assert config.host == "localhost"
        assert config.port == 8000
        assert config.enable_bilingual_output is True

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict('os.environ', {
            'MCP_HOST': '0.0.0.0',
            'MCP_PORT': '9000',
            'MCP_DEFAULT_LANGUAGE': 'zh'
        }):
            config = MCPServerConfig.from_env()

            assert config.host == '0.0.0.0'
            assert config.port == 9000
            assert config.default_language == 'zh'


class TestRestaurantFinancialMCPServer:
    """Test the main MCP server implementation."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPServerConfig(
            server_name="test-server",
            log_level="DEBUG",
            max_file_size_mb=10
        )

    @pytest.fixture
    def server(self, config):
        """Create test server instance."""
        return RestaurantFinancialMCPServer(config)

    def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.config.server_name == "test-server"
        assert server.analytics_engine is not None
        assert server.parser is not None
        assert server.validator is not None

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test tool listing functionality."""
        tools = await server.server.list_tools()

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "parse_excel",
            "validate_financial_data",
            "calculate_kpis",
            "analyze_trends",
            "generate_insights",
            "comprehensive_analysis"
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_list_resources(self, server):
        """Test resource listing functionality."""
        resources = await server.server.list_resources()

        assert len(resources) >= 2
        resource_names = [resource.name for resource in resources]
        assert "Sample Restaurant Data" in resource_names
        assert "API Documentation" in resource_names

    @pytest.mark.asyncio
    async def test_parse_excel_tool_success(self, server):
        """Test successful Excel parsing tool call."""
        # Create a temporary Excel file for testing
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Mock the parser to return test data
            with patch.object(server.parser, 'parse_income_statement') as mock_parse:
                mock_parse.return_value = {
                    'periods': ['2024Q1'],
                    'financial_data': {
                        '2024Q1': {
                            'revenue': {'total': 150000, 'food': 120000, 'beverage': 25000, 'other': 5000},
                            'costs': {'total': 52500, 'food': 45000, 'beverage': 7500},
                            'expenses': {'total': 75000, 'labor': 45000, 'rent': 15000}
                        }
                    }
                }

                # Call the tool
                result = await server._handle_parse_excel({"file_path": tmp_path})

                assert result["success"] is True
                assert result["file_path"] == tmp_path
                assert "periods" in result
                assert "financial_data" in result

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_parse_excel_tool_file_not_found(self, server):
        """Test Excel parsing tool with non-existent file."""
        with pytest.raises(FileNotFoundError):
            await server._handle_parse_excel({"file_path": "/non/existent/file.xlsx"})

    @pytest.mark.asyncio
    async def test_comprehensive_analysis_tool(self, server):
        """Test comprehensive analysis tool."""
        # Create a temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Mock the analytics engine
            with patch.object(server.analytics_engine, 'analyze_restaurant_excel') as mock_analyze:
                mock_result = Mock()
                mock_result.to_dict = Mock(return_value={
                    "restaurant_name": "Test Restaurant",
                    "analysis_date": "2024-01-01",
                    "kpis": {"profitability": {"gross_margin": 65.0}},
                    "insights": {"strengths": ["Good cost control"]}
                })
                mock_analyze.return_value = mock_result

                result = await server._handle_comprehensive_analysis({
                    "file_path": tmp_path,
                    "language": "en"
                })

                assert result["success"] is True
                assert "analysis" in result
                assert result["language"] == "en"

        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestClaudeCodeIntegration:
    """Test Claude Code integration functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPServerConfig(
            claude_code_enabled=True,
            claude_code_endpoint="http://localhost:8080"
        )

    @pytest.fixture
    def integration(self, config):
        """Create Claude Code integration instance."""
        return ClaudeCodeIntegration(config)

    @pytest.mark.asyncio
    async def test_initialization(self, integration):
        """Test Claude Code integration initialization."""
        with patch.object(integration.mcp_server, 'start') as mock_start:
            mock_start.return_value = None
            await integration.initialize()

            assert integration.connected is True
            assert integration.session_id is not None

    @pytest.mark.asyncio
    async def test_tool_call_handling(self, integration):
        """Test handling tool calls from Claude Code."""
        # Mock the MCP server tool call
        with patch.object(integration.mcp_server.server, 'call_tool') as mock_call:
            mock_call.return_value = [{"result": "success"}]

            request = {
                "type": "tool_call",
                "tool_name": "parse_excel",
                "arguments": {"file_path": "/test/file.xlsx"}
            }

            result = await integration.handle_claude_request(request)

            assert result["success"] is True
            assert result["tool_name"] == "parse_excel"
            assert "results" in result

    @pytest.mark.asyncio
    async def test_prompt_generation(self, integration):
        """Test prompt response generation."""
        arguments = {"language": "en"}
        response = await integration._generate_analysis_prompt_response(arguments)

        assert "Restaurant Financial Analysis Report Generation" in response
        assert "KPIs" in response

    @pytest.mark.asyncio
    async def test_bilingual_report_generation(self, integration):
        """Test bilingual report generation."""
        analysis_data = {
            "kpis": {"profitability": {"gross_margin": 65.0}},
            "insights": {"strengths": ["Strong performance"]}
        }

        result = await integration.generate_bilingual_report(analysis_data)

        assert "english" in result
        assert "chinese" in result
        assert result["bilingual"] is True


class TestBilingualReportGenerator:
    """Test bilingual report generation."""

    @pytest.fixture
    def generator(self):
        """Create report generator instance."""
        return BilingualReportGenerator()

    def test_chinese_terms_loading(self, generator):
        """Test Chinese terms mapping."""
        assert "revenue" in generator.chinese_terms
        assert generator.chinese_terms["revenue"] == "营业收入"
        assert generator.chinese_terms["profit"] == "利润"

    def test_report_generation_english(self, generator):
        """Test English report generation."""
        analysis_data = {
            "kpis": {
                "profitability": {"gross_margin": 65.0, "operating_margin": 15.0, "net_margin": 10.0},
                "efficiency": {"food_cost_percentage": 30.0, "labor_cost_percentage": 28.0, "prime_cost_ratio": 58.0}
            },
            "insights": {
                "strengths": ["Strong cost control"],
                "areas_for_improvement": ["Revenue growth"],
                "recommendations": ["Optimize menu pricing"]
            }
        }

        report = generator.generate_comprehensive_report(
            "Test Restaurant",
            analysis_data,
            ReportLanguage.ENGLISH,
            ReportFormat.MARKDOWN
        )

        assert "Test Restaurant Financial Analysis Report" in report
        assert "Key Performance Indicators" in report
        assert "Business Insights" in report
        assert "65.0%" in report

    def test_report_generation_chinese(self, generator):
        """Test Chinese report generation."""
        analysis_data = {
            "kpis": {
                "profitability": {"gross_margin": 65.0, "operating_margin": 15.0, "net_margin": 10.0},
                "efficiency": {"food_cost_percentage": 30.0, "labor_cost_percentage": 28.0, "prime_cost_ratio": 58.0}
            },
            "insights": {
                "strengths": ["成本控制良好"],
                "areas_for_improvement": ["提升收入增长"],
                "recommendations": ["优化菜单定价"]
            }
        }

        report = generator.generate_comprehensive_report(
            "测试餐厅",
            analysis_data,
            ReportLanguage.CHINESE,
            ReportFormat.MARKDOWN
        )

        assert "测试餐厅 财务分析报告" in report
        assert "关键绩效指标" in report
        assert "经营洞察" in report
        assert "65.0%" in report

    def test_report_generation_bilingual(self, generator):
        """Test bilingual report generation."""
        analysis_data = {
            "kpis": {
                "profitability": {"gross_margin": 65.0},
                "efficiency": {"food_cost_percentage": 30.0}
            },
            "insights": {
                "strengths": ["Strong performance"],
                "areas_for_improvement": ["Revenue optimization"],
                "recommendations": ["Menu engineering"]
            }
        }

        report = generator.generate_comprehensive_report(
            "Test Restaurant",
            analysis_data,
            ReportLanguage.BILINGUAL,
            ReportFormat.MARKDOWN
        )

        # Should contain both English and Chinese content
        assert "Financial Analysis Report" in report
        assert "财务分析报告" in report
        assert "Key Performance Indicators" in report
        assert "关键绩效指标" in report

    def test_json_format_output(self, generator):
        """Test JSON format output."""
        analysis_data = {
            "kpis": {"profitability": {"gross_margin": 65.0}},
            "insights": {"strengths": ["Good performance"]}
        }

        result = generator.generate_comprehensive_report(
            "Test Restaurant",
            analysis_data,
            ReportLanguage.ENGLISH,
            ReportFormat.JSON
        )

        assert isinstance(result, dict)
        assert "report_text" in result
        assert "analysis_data" in result
        assert result["format"] == "json"


class TestErrorHandling:
    """Test error handling and recovery mechanisms."""

    @pytest.fixture
    def error_manager(self):
        """Create error recovery manager instance."""
        return ErrorRecoveryManager()

    @pytest.fixture
    def error_context(self):
        """Create test error context."""
        return ErrorContext(
            tool_name="parse_excel",
            file_path="/test/file.xlsx",
            user_input={"file_path": "/test/file.xlsx"}
        )

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, error_manager, error_context):
        """Test validation error handling."""
        error = ValueError("Invalid data format")

        result = await error_manager.handle_error(error, error_context)

        assert "error" in result
        assert result["error"]["category"] == "validation"
        assert result["recovery_attempted"] is True

    @pytest.mark.asyncio
    async def test_file_not_found_error_handling(self, error_manager, error_context):
        """Test file not found error handling."""
        error = FileNotFoundError("File not found")

        result = await error_manager.handle_error(error, error_context)

        assert result["error"]["category"] == "parsing"
        assert result["error"]["severity"] in ["low", "medium"]

    @pytest.mark.asyncio
    async def test_network_error_recovery(self, error_manager, error_context):
        """Test network error recovery with retry."""
        error = ConnectionError("Network unavailable")

        with patch('asyncio.sleep') as mock_sleep:
            result = await error_manager.handle_error(error, error_context, retry_count=1)

            assert result["error"]["category"] == "network"
            assert result["recovery_attempted"] is True

    def test_error_categorization(self, error_manager, error_context):
        """Test error categorization logic."""
        # Test different error types
        validation_error = ValueError("Validation failed")
        file_error = FileNotFoundError("File not found")
        network_error = ConnectionError("Connection failed")

        val_category = error_manager._categorize_error(validation_error, error_context)
        file_category = error_manager._categorize_error(file_error, error_context)
        net_category = error_manager._categorize_error(network_error, error_context)

        assert val_category == ErrorCategory.ANALYSIS  # ValueError falls under analysis
        assert file_category == ErrorCategory.PARSING
        assert net_category == ErrorCategory.NETWORK

    def test_suggested_actions_generation(self, error_manager, error_context):
        """Test suggested actions generation."""
        error = ValueError("Invalid format")
        category = ErrorCategory.VALIDATION

        actions = error_manager._generate_suggested_actions(error, category, error_context)

        assert len(actions) > 0
        assert any("Check input data format" in action for action in actions)
        assert any("Review error details" in action for action in actions)


class TestIntegrationScenarios:
    """Test end-to-end integration scenarios."""

    @pytest.fixture
    def config(self):
        """Create integration test configuration."""
        return MCPServerConfig(
            server_name="integration-test",
            enable_bilingual_output=True,
            log_level="DEBUG"
        )

    @pytest.mark.asyncio
    async def test_end_to_end_excel_analysis(self, config):
        """Test complete end-to-end Excel analysis workflow."""
        server = RestaurantFinancialMCPServer(config)

        # Create sample Excel data
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Mock the analytics engine for complete workflow
            with patch.object(server.analytics_engine, 'analyze_restaurant_excel') as mock_analyze:
                mock_result = Mock()
                mock_result.to_dict = Mock(return_value={
                    "restaurant_name": "Integration Test Restaurant",
                    "analysis_date": "2024-01-01",
                    "periods_analyzed": ["2024Q1"],
                    "kpis": {
                        "profitability": {"gross_margin": 65.0, "operating_margin": 15.0},
                        "efficiency": {"food_cost_percentage": 30.0, "labor_cost_percentage": 28.0}
                    },
                    "insights": {
                        "strengths": ["Excellent cost control", "Strong profitability"],
                        "areas_for_improvement": ["Revenue diversification", "Menu optimization"],
                        "recommendations": ["Expand catering services", "Implement dynamic pricing"]
                    }
                })
                mock_analyze.return_value = mock_result

                # Test the comprehensive analysis tool
                result = await server._handle_comprehensive_analysis({
                    "file_path": tmp_path,
                    "language": "both",
                    "include_executive_summary": True
                })

                # Verify the complete analysis result
                assert result["success"] is True
                assert "analysis" in result
                assert result["language"] == "both"

                analysis = result["analysis"]
                assert analysis["restaurant_name"] == "Integration Test Restaurant"
                assert "kpis" in analysis
                assert "insights" in analysis

                # Verify KPIs
                kpis = analysis["kpis"]
                assert kpis["profitability"]["gross_margin"] == 65.0
                assert kpis["efficiency"]["food_cost_percentage"] == 30.0

                # Verify insights
                insights = analysis["insights"]
                assert len(insights["strengths"]) == 2
                assert len(insights["recommendations"]) == 2

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, config):
        """Test error recovery in a realistic workflow."""
        server = RestaurantFinancialMCPServer(config)
        error_manager = ErrorRecoveryManager()

        # Simulate a parsing error followed by recovery
        context = ErrorContext(
            tool_name="comprehensive_analysis",
            file_path="/non/existent/file.xlsx"
        )

        # Test error handling
        error = FileNotFoundError("Excel file not found")
        error_result = await error_manager.handle_error(error, context)

        assert error_result["error"]["category"] == "parsing"
        assert error_result["recovery_attempted"] is True
        assert len(error_result["error"]["suggested_actions"]) > 0

    @pytest.mark.asyncio
    async def test_bilingual_output_integration(self, config):
        """Test bilingual output in complete workflow."""
        server = RestaurantFinancialMCPServer(config)
        integration = ClaudeCodeIntegration(config)

        # Test bilingual report generation
        analysis_data = {
            "restaurant_name": "国际餐厅 International Restaurant",
            "kpis": {
                "profitability": {"gross_margin": 68.5, "operating_margin": 18.2},
                "efficiency": {"food_cost_percentage": 31.5, "prime_cost_ratio": 59.5}
            },
            "insights": {
                "strengths": ["优秀的成本控制 / Excellent cost control", "稳定的盈利能力 / Stable profitability"],
                "areas_for_improvement": ["市场营销 / Marketing efforts", "数字化升级 / Digital transformation"],
                "recommendations": ["实施会员计划 / Implement loyalty program", "优化在线订购 / Optimize online ordering"]
            }
        }

        bilingual_report = await integration.generate_bilingual_report(analysis_data)

        assert bilingual_report["bilingual"] is True
        assert "english" in bilingual_report
        assert "chinese" in bilingual_report

        # Verify both versions contain key information
        english_report = bilingual_report["english"]
        chinese_report = bilingual_report["chinese"]

        assert "Financial Analysis Report" in english_report
        assert "财务分析报告" in chinese_report
        assert "68.5%" in english_report
        assert "68.5%" in chinese_report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])