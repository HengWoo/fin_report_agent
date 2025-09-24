"""
Legacy Analysis Handler

Handles legacy financial analysis tools for backward compatibility.
Extracted from server.py lines 514-780.
"""

from typing import Dict, Any
from pathlib import Path
from mcp.types import TextContent
from .base import BaseHandler


class LegacyAnalysisHandler(BaseHandler):
    """Handler for legacy financial analysis tools."""

    async def handle_parse_excel(self, arguments: Dict[str, Any]) -> TextContent:
        """
        Handle Excel parsing tool call.

        NEW: Now uses AccountHierarchyParser with column intelligence instead of ChineseExcelParser
        to prevent double counting and exclude non-financial columns.
        """
        file_path = arguments.get("file_path")
        sheet_name = arguments.get("sheet_name")

        if not file_path:
            return self.format_error("file_path is required", "parse_excel")

        if not Path(file_path).exists():
            return self.format_error(f"File not found: {file_path}", "parse_excel")

        try:
            hierarchy_parser = self.context.get("hierarchy_parser")
            if not hierarchy_parser:
                return self.format_error(
                    "hierarchy_parser not available", "parse_excel"
                )

            hierarchy_result = hierarchy_parser.parse_hierarchy(file_path)

            if hierarchy_result.get("parsing_status") == "success":
                accounts = hierarchy_result.get("accounts", [])
                column_intelligence = hierarchy_result.get("column_intelligence", {})

                value_columns = column_intelligence.get("value_columns", [])
                subtotal_columns = column_intelligence.get("subtotal_columns", [])
                excluded = column_intelligence.get("excluded_columns", {})

                output = "📊 Excel文件解析成功 (智能列识别)\n"
                output += f"文件路径: {file_path}\n"
                output += f"发现账户: {len(accounts)} 个\n"

                output += "\n🧠 列智能分析:\n"
                output += f"• 数值列: {len(value_columns)} 个\n"
                output += f"• 小计列: {len(subtotal_columns)} 个 (用于值，不参与求和)\n"

                total_excluded = sum(len(cols) for cols in excluded.values())
                if total_excluded > 0:
                    output += f"• 排除列: {total_excluded} 个\n"
                    if excluded.get("notes"):
                        output += f"  - 备注列: {len(excluded['notes'])} 个\n"
                    if excluded.get("ratios"):
                        output += f"  - 占比列: {len(excluded['ratios'])} 个\n"
                    if excluded.get("subtotals"):
                        output += f"  - 小计列: {len(excluded['subtotals'])} 个 (防止重复计算)\n"

                if accounts:
                    output += "\n主要账户示例:\n"
                    for account in accounts[:5]:
                        name = account.get("name", "")
                        value = account.get("total_value", 0)
                        used_subtotal = account.get("used_subtotal", False)
                        marker = " ✓(小计)" if used_subtotal else ""
                        output += f"• {name}: ¥{value:,.2f}{marker}\n"
                    if len(accounts) > 5:
                        output += f"• ... 还有 {len(accounts) - 5} 个账户\n"

                col_report = column_intelligence.get("classification_report", "")
                if col_report:
                    output += "\n" + "=" * 50 + "\n"
                    output += col_report

                return self.format_success(output)
            else:
                error_msg = hierarchy_result.get("error", "Unknown parsing error")
                return self.format_error(error_msg, "parse_excel")

        except Exception as e:
            return self.format_error(str(e), "parse_excel")

    async def handle_validate_financial_data(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle financial data validation tool call."""
        financial_data = arguments.get("financial_data")
        strict_mode = arguments.get("strict_mode", False)

        if not financial_data:
            return self.format_error(
                "financial_data is required", "validate_financial_data"
            )

        try:
            validator = self.context.get("validator")
            if not validator:
                return self.format_error(
                    "validator not available", "validate_financial_data"
                )

            validation_results = validator.validate_restaurant_data(financial_data)

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

            return self.format_success(output)

        except Exception as e:
            return self.format_error(str(e), "validate_financial_data")

    async def handle_calculate_kpis(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle KPI calculation tool call."""
        income_statement_data = arguments.get("income_statement")
        include_benchmarks = arguments.get("include_benchmarks", True)

        if not income_statement_data:
            return self.format_error("income_statement is required", "calculate_kpis")

        try:
            analytics_engine = self.context.get("analytics_engine")
            if not analytics_engine:
                return self.format_error(
                    "analytics_engine not available", "calculate_kpis"
                )

            kpis = analytics_engine.calculate_kpis(income_statement_data)

            output = "📊 餐厅关键绩效指标 (KPI) 分析\n"
            output += "=" * 40 + "\n"

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

            if include_benchmarks:
                output += "\n🏭 行业基准对比:\n"
                output += "• 毛利率目标: 60-70%\n"
                output += "• 食品成本率: 28-35%\n"
                output += "• 人工成本率: 25-35%\n"
                output += "• 主成本率: <60%\n"

            return self.format_success(output)

        except Exception as e:
            return self.format_error(str(e), "calculate_kpis")

    async def handle_analyze_trends(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle trend analysis tool call."""
        historical_statements = arguments.get("historical_statements")
        include_forecasting = arguments.get("include_forecasting", True)

        if not historical_statements:
            return self.format_error(
                "historical_statements is required", "analyze_trends"
            )

        if len(historical_statements) < 2:
            return self.format_error(
                "At least 2 historical statements required for trend analysis",
                "analyze_trends",
            )

        try:
            analytics_engine = self.context.get("analytics_engine")
            if not analytics_engine:
                return self.format_error(
                    "analytics_engine not available", "analyze_trends"
                )

            trends = analytics_engine.analyze_trends(historical_statements)

            output = "📈 趋势分析报告\n"
            output += "=" * 30 + "\n"
            output += f"分析期间: {len(historical_statements)} 个时间段\n"
            output += f"预测功能: {'开启' if include_forecasting else '关闭'}\n\n"

            if "revenue_trend" in trends:
                revenue_trend = trends["revenue_trend"]
                growth_rate = revenue_trend.get("growth_rate", 0) * 100
                direction = (
                    "📈 上升"
                    if growth_rate > 5
                    else "📉 下降" if growth_rate < -5 else "➡️ 稳定"
                )
                output += f"营业收入趋势: {direction} ({growth_rate:+.1f}%)\n"

            if "cost_trends" in trends:
                cost_trends = trends["cost_trends"]
                output += "\n💸 成本趋势:\n"
                for cost_type, trend_data in cost_trends.items():
                    if isinstance(trend_data, dict) and "growth_rate" in trend_data:
                        rate = trend_data["growth_rate"] * 100
                        output += f"• {cost_type}: {rate:+.1f}%\n"

            if include_forecasting and "forecast" in trends:
                forecast = trends["forecast"]
                output += "\n🔮 预测分析:\n"
                output += (
                    f"• 下期收入预测: {forecast.get('next_period_revenue', 'N/A')}\n"
                )
                output += f"• 增长预期: {forecast.get('growth_expectation', 'N/A')}\n"

            return self.format_success(output)

        except Exception as e:
            return self.format_error(str(e), "analyze_trends")

    async def handle_generate_insights(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle insights generation tool call."""
        kpis = arguments.get("kpis")
        income_statement = arguments.get("income_statement")
        language = arguments.get("language", "both")

        if not kpis:
            return self.format_error("kpis is required", "generate_insights")
        if not income_statement:
            return self.format_error(
                "income_statement is required", "generate_insights"
            )

        try:
            analytics_engine = self.context.get("analytics_engine")
            config = self.context.get("config")
            if not analytics_engine:
                return self.format_error(
                    "analytics_engine not available", "generate_insights"
                )

            insights = analytics_engine.generate_insights(kpis, income_statement)

            output = "💡 经营洞察与建议\n"
            output += "=" * 35 + "\n"

            strengths = insights.get("strengths", [])
            if strengths:
                output += "\n✅ 经营优势:\n"
                for i, strength in enumerate(strengths[:5], 1):
                    output += f"{i}. {strength}\n"

            improvements = insights.get("areas_for_improvement", [])
            if improvements:
                output += "\n⚠️ 改进领域:\n"
                for i, improvement in enumerate(improvements[:5], 1):
                    output += f"{i}. {improvement}\n"

            recommendations = insights.get("recommendations", [])
            if recommendations:
                output += "\n🎯 具体建议:\n"
                for i, rec in enumerate(recommendations[:5], 1):
                    output += f"{i}. {rec}\n"

            if language == "both" and config and config.enable_bilingual_output:
                output += "\n[双语分析完成 / Bilingual analysis completed]\n"

            return self.format_success(output)

        except Exception as e:
            return self.format_error(str(e), "generate_insights")
