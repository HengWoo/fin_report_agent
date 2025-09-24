"""
Claude Code Integration Module

This module provides integration between the Restaurant Financial Analysis
MCP Server and Claude Code, enabling seamless AI-powered financial analysis.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .config import MCPServerConfig
from .server import RestaurantFinancialMCPServer


class ClaudeCodeIntegration:
    """Integration handler for Claude Code."""

    def __init__(self, config: MCPServerConfig):
        """Initialize Claude Code integration."""
        self.config = config
        self.logger = logging.getLogger(f"{config.server_name}.claude_integration")
        self.mcp_server = RestaurantFinancialMCPServer(config)

        # Integration state
        self.connected = False
        self.session_id: Optional[str] = None
        self.capabilities: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize the Claude Code integration."""
        self.logger.info("Initializing Claude Code integration")

        try:
            # Start the MCP server
            await self.mcp_server.start()

            # Register with Claude Code (if endpoint is provided)
            if self.config.claude_code_endpoint:
                await self._register_with_claude_code()

            self.connected = True
            self.logger.info("Claude Code integration initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Claude Code integration: {str(e)}")
            raise

    async def _register_with_claude_code(self) -> None:
        """Register this MCP server with Claude Code."""
        registration_data = {
            "server_name": self.config.server_name,
            "server_version": self.config.server_version,
            "description": self.config.description,
            "capabilities": {
                "tools": await self._get_tool_capabilities(),
                "resources": await self._get_resource_capabilities(),
                "prompts": await self._get_prompt_capabilities(),
            },
            "metadata": {
                "language_support": ["en", "zh"],
                "file_types": self.config.allowed_file_extensions,
                "max_file_size_mb": self.config.max_file_size_mb,
            },
        }

        self.logger.info(f"Registering with Claude Code: {registration_data}")
        # In a real implementation, this would make an HTTP request to Claude Code
        # For now, we'll simulate the registration
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.capabilities = registration_data["capabilities"]

    async def _get_tool_capabilities(self) -> List[Dict[str, Any]]:
        """Get tool capabilities for registration."""
        tools = await self.mcp_server.server.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": self._categorize_tool(tool.name),
                "complexity": self._assess_tool_complexity(tool.name),
                "estimated_duration": self._estimate_tool_duration(tool.name),
            }
            for tool in tools
        ]

    async def _get_resource_capabilities(self) -> List[Dict[str, Any]]:
        """Get resource capabilities for registration."""
        resources = await self.mcp_server.server.list_resources()
        return [
            {
                "uri": str(resource.uri),
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mimeType,
            }
            for resource in resources
        ]

    async def _get_prompt_capabilities(self) -> List[Dict[str, Any]]:
        """Get prompt capabilities for registration."""
        return [
            {
                "name": "restaurant_analysis_prompt",
                "description": "Generate comprehensive restaurant financial analysis reports",
                "languages": ["en", "zh"],
                "output_formats": ["text", "json", "markdown"],
            },
            {
                "name": "kpi_explanation_prompt",
                "description": "Explain restaurant KPIs and their business implications",
                "languages": ["en", "zh"],
                "output_formats": ["text", "markdown"],
            },
            {
                "name": "trend_analysis_prompt",
                "description": "Analyze and explain financial trends over time",
                "languages": ["en", "zh"],
                "output_formats": ["text", "markdown"],
            },
        ]

    def _categorize_tool(self, tool_name: str) -> str:
        """Categorize a tool for Claude Code."""
        categories = {
            "parse_excel": "data_processing",
            "validate_financial_data": "data_validation",
            "calculate_kpis": "analysis",
            "analyze_trends": "analysis",
            "generate_insights": "ai_generation",
            "comprehensive_analysis": "end_to_end",
        }
        return categories.get(tool_name, "general")

    def _assess_tool_complexity(self, tool_name: str) -> str:
        """Assess tool complexity for Claude Code."""
        complexity_map = {
            "parse_excel": "medium",
            "validate_financial_data": "low",
            "calculate_kpis": "medium",
            "analyze_trends": "high",
            "generate_insights": "high",
            "comprehensive_analysis": "very_high",
        }
        return complexity_map.get(tool_name, "medium")

    def _estimate_tool_duration(self, tool_name: str) -> int:
        """Estimate tool execution duration in seconds."""
        duration_map = {
            "parse_excel": 30,
            "validate_financial_data": 10,
            "calculate_kpis": 20,
            "analyze_trends": 45,
            "generate_insights": 60,
            "comprehensive_analysis": 120,
        }
        return duration_map.get(tool_name, 30)

    async def handle_claude_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request from Claude Code."""
        self.logger.info(
            f"Handling Claude Code request: {request.get('type', 'unknown')}"
        )

        try:
            request_type = request.get("type")

            if request_type == "tool_call":
                return await self._handle_tool_call(request)
            elif request_type == "resource_request":
                return await self._handle_resource_request(request)
            elif request_type == "prompt_request":
                return await self._handle_prompt_request(request)
            else:
                raise ValueError(f"Unknown request type: {request_type}")

        except Exception as e:
            self.logger.error(f"Error handling Claude request: {str(e)}")
            return {"success": False, "error": str(e), "error_type": type(e).__name__}

    async def _handle_tool_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call from Claude Code."""
        tool_name = request.get("tool_name")
        arguments = request.get("arguments", {})

        # Call the tool through the MCP server
        results = await self.mcp_server.server.call_tool(tool_name, arguments)

        return {
            "success": True,
            "tool_name": tool_name,
            "results": results,
            "execution_time": datetime.now().isoformat(),
        }

    async def _handle_resource_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a resource request from Claude Code."""
        resource_uri = request.get("resource_uri")

        # Get resource content
        # In a real implementation, this would fetch the actual resource
        return {
            "success": True,
            "resource_uri": resource_uri,
            "content": "Resource content would be here",
            "mime_type": "text/plain",
        }

    async def _handle_prompt_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a prompt request from Claude Code."""
        prompt_name = request.get("prompt_name")
        arguments = request.get("arguments", {})

        # Generate prompt response
        response = await self._generate_prompt_response(prompt_name, arguments)

        return {
            "success": True,
            "prompt_name": prompt_name,
            "response": response,
            "language": arguments.get("language", "en"),
        }

    async def _generate_prompt_response(
        self, prompt_name: str, arguments: Dict[str, Any]
    ) -> str:
        """Generate response for a specific prompt."""
        if prompt_name == "restaurant_analysis_prompt":
            return await self._generate_analysis_prompt_response(arguments)
        elif prompt_name == "kpi_explanation_prompt":
            return await self._generate_kpi_explanation_response(arguments)
        elif prompt_name == "trend_analysis_prompt":
            return await self._generate_trend_explanation_response(arguments)
        else:
            return f"Unknown prompt: {prompt_name}"

    async def _generate_analysis_prompt_response(
        self, arguments: Dict[str, Any]
    ) -> str:
        """Generate comprehensive analysis prompt response."""
        language = arguments.get("language", "en")

        if language == "zh":
            return """
# 餐厅财务分析报告生成

基于提供的财务数据，我将为您生成一份全面的餐厅财务分析报告，包括：

## 分析内容
1. **关键绩效指标 (KPIs)** - 盈利能力、运营效率、增长指标
2. **趋势分析** - 多期间财务表现对比
3. **行业基准对比** - 与餐饮行业标准的比较
4. **经营洞察** - 优势识别和改进建议
5. **行动计划** - 具体的业务改进措施

## 输出格式
- 中英双语报告
- 可视化图表说明
- 关键指标总结
- 执行建议清单

请提供您的财务数据，我将立即开始分析。
            """
        else:
            return """
# Restaurant Financial Analysis Report Generation

Based on the provided financial data, I will generate a comprehensive restaurant financial analysis report including:

## Analysis Components
1. **Key Performance Indicators (KPIs)** - Profitability, efficiency, growth metrics
2. **Trend Analysis** - Multi-period financial performance comparison
3. **Industry Benchmarking** - Comparison against restaurant industry standards
4. **Business Insights** - Strengths identification and improvement recommendations
5. **Action Plan** - Specific business improvement measures

## Output Format
- Bilingual report (Chinese-English)
- Visual chart explanations
- Key metrics summary
- Executive action items

Please provide your financial data and I will begin the analysis immediately.
            """

    async def _generate_kpi_explanation_response(
        self, arguments: Dict[str, Any]
    ) -> str:
        """Generate KPI explanation response."""
        language = arguments.get("language", "en")

        if language == "zh":
            return """
# 餐厅关键绩效指标 (KPIs) 解释

## 盈利能力指标
- **毛利率**: 反映菜品定价和成本控制效果
- **营业利润率**: 衡量整体运营效率
- **净利润率**: 最终盈利能力指标

## 运营效率指标
- **食品成本率**: 行业标准 28-35%
- **人工成本率**: 行业标准 25-35%
- **主要成本率**: 食品+人工，目标 <60%

## 增长指标
- **收入增长率**: 同比和环比增长
- **客流量变化**: 市场份额指标
- **平均客单价**: 服务价值体现

每个指标的具体含义和改进方法将在分析中详细说明。
            """
        else:
            return """
# Restaurant Key Performance Indicators (KPIs) Explanation

## Profitability Metrics
- **Gross Margin**: Reflects pricing strategy and cost control effectiveness
- **Operating Margin**: Measures overall operational efficiency
- **Net Margin**: Final profitability indicator

## Operational Efficiency Metrics
- **Food Cost %**: Industry standard 28-35%
- **Labor Cost %**: Industry standard 25-35%
- **Prime Cost %**: Food + Labor, target <60%

## Growth Metrics
- **Revenue Growth Rate**: Year-over-year and period-over-period growth
- **Customer Traffic Changes**: Market share indicators
- **Average Ticket Size**: Service value representation

Specific meanings and improvement methods for each indicator will be detailed in the analysis.
            """

    async def _generate_trend_explanation_response(
        self, arguments: Dict[str, Any]
    ) -> str:
        """Generate trend analysis explanation response."""
        language = arguments.get("language", "en")

        if language == "zh":
            return """
# 财务趋势分析说明

## 趋势分析方法
1. **环比分析**: 连续期间的变化情况
2. **同比分析**: 同一时期的年度对比
3. **移动平均**: 平滑季节性波动
4. **趋势预测**: 基于历史数据的未来预期

## 关键趋势指标
- **收入趋势**: 增长、稳定或下降
- **成本趋势**: 成本控制效果
- **利润趋势**: 盈利能力变化
- **效率趋势**: 运营改善情况

## 趋势警示信号
- 连续下降的毛利率
- 持续上升的成本率
- 客流量减少趋势
- 季节性异常变化

趋势分析帮助识别业务发展方向和潜在风险。
            """
        else:
            return """
# Financial Trend Analysis Explanation

## Trend Analysis Methods
1. **Period-over-Period Analysis**: Changes between consecutive periods
2. **Year-over-Year Analysis**: Annual comparisons for same periods
3. **Moving Averages**: Smoothing seasonal fluctuations
4. **Trend Forecasting**: Future expectations based on historical data

## Key Trend Indicators
- **Revenue Trends**: Growth, stability, or decline patterns
- **Cost Trends**: Cost control effectiveness
- **Profit Trends**: Profitability evolution
- **Efficiency Trends**: Operational improvement progress

## Trend Warning Signals
- Consecutive declining gross margins
- Persistently rising cost ratios
- Declining customer traffic trends
- Seasonal anomalies

Trend analysis helps identify business direction and potential risks.
            """

    async def generate_bilingual_report(
        self, analysis_data: Dict[str, Any], report_type: str = "comprehensive"
    ) -> Dict[str, str]:
        """Generate bilingual analysis report."""
        self.logger.info(f"Generating bilingual report: {report_type}")

        try:
            # Generate English version
            english_report = await self._generate_english_report(
                analysis_data, report_type
            )

            # Generate Chinese version
            chinese_report = await self._generate_chinese_report(
                analysis_data, report_type
            )

            return {
                "english": english_report,
                "chinese": chinese_report,
                "bilingual": True,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to generate bilingual report: {str(e)}")
            raise

    async def _generate_english_report(
        self, analysis_data: Dict[str, Any], report_type: str
    ) -> str:
        """Generate English version of the report."""
        # This would contain sophisticated report generation logic
        return f"""
# Restaurant Financial Analysis Report

## Executive Summary
This comprehensive analysis reveals key insights into restaurant performance...

## Key Performance Indicators
- Gross Margin: [Value]%
- Operating Margin: [Value]%
- Food Cost %: [Value]%
- Labor Cost %: [Value]%

## Trends and Insights
[Detailed analysis based on data]

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

Generated by Restaurant Financial Analysis MCP Server v{self.config.server_version}
        """

    async def _generate_chinese_report(
        self, analysis_data: Dict[str, Any], report_type: str
    ) -> str:
        """Generate Chinese version of the report."""
        return f"""
# 餐厅财务分析报告

## 执行摘要
本次综合分析揭示了餐厅经营的关键洞察...

## 关键绩效指标
- 毛利率: [数值]%
- 营业利润率: [数值]%
- 食品成本率: [数值]%
- 人工成本率: [数值]%

## 趋势与洞察
[基于数据的详细分析]

## 改进建议
1. [建议一]
2. [建议二]
3. [建议三]

由餐厅财务分析MCP服务器 v{self.config.server_version} 生成
        """

    async def shutdown(self) -> None:
        """Shutdown the Claude Code integration."""
        self.logger.info("Shutting down Claude Code integration")

        try:
            # Stop the MCP server
            await self.mcp_server.stop()

            self.connected = False
            self.session_id = None

            self.logger.info("Claude Code integration shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
            raise
