"""
Complex Analysis Handler

Handles complex financial analysis workflows.
Extracted from server.py lines 783-1067.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from mcp.types import TextContent
from .base import BaseHandler


class ComplexAnalysisHandler(BaseHandler):
    """Handler for complex financial analysis tools."""

    async def handle_comprehensive_analysis(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """
        Handle comprehensive analysis using Claude Orchestrator.

        This leverages Claude's intelligence through the orchestration layer
        to perform sophisticated financial analysis without hardcoded rules.
        """
        file_path = arguments.get("file_path")
        language = arguments.get("language", "both")
        include_executive_summary = arguments.get("include_executive_summary", True)

        if not file_path:
            return self.format_error("file_path is required", "comprehensive_analysis")

        if not Path(file_path).exists():
            return self.format_error(f"File not found: {file_path}", "comprehensive_analysis")

        try:
            orchestrator = self.context.get("orchestrator")
            validation_state_manager = self.context.get("validation_state_manager")

            if not orchestrator:
                return self.format_error("orchestrator not available", "comprehensive_analysis")

            self.logger.info(f"Starting orchestrated analysis of {file_path}")

            analysis_result = orchestrator.analyze_financial_report(file_path)

            if analysis_result.get("validation_required"):
                output = "⚠️ 验证要求 - 必须先完成账户结构验证\n"
                output += "=" * 50 + "\n"
                output += f"📁 文件: {file_path}\n"
                output += f"状态: {analysis_result.get('status', 'validation_required')}\n\n"

                output += f"💡 {analysis_result.get('message', 'Account structure validation required')}\n\n"

                if analysis_result.get("hierarchy"):
                    output += "📊 发现账户结构:\n"
                    output += f"• 总账户数: {analysis_result.get('total_accounts', 0)}\n"
                    output += f"• 安全计算账户: {analysis_result.get('safe_accounts_count', 0)}\n"
                    output += f"• 潜在重复计算风险: {analysis_result.get('potential_issues', 0)}\n\n"

                output += "🔧 下一步操作:\n"
                for step in analysis_result.get("next_steps", []):
                    output += f"   {step}\n"

                output += "\n⚡ 请运行 validate_account_structure 工具完成验证！"

                return self.format_success(output)

            if analysis_result.get("error"):
                return self.format_error(analysis_result["error"], "comprehensive_analysis")

            report_type = analysis_result.get("report_type", "Unknown")
            periods = analysis_result.get("periods", [])
            calculations = analysis_result.get("calculations", {})
            validation = analysis_result.get("validation", {})
            warnings = analysis_result.get("warnings", [])

            output = "🏪 餐厅财务综合分析报告 (Claude Orchestrated)\n"
            output += "=" * 50 + "\n"
            output += f"📁 文件: {file_path}\n"
            output += f"📈 报表类型: {report_type}\n"
            output += f"📅 分析期间: {', '.join(periods)}\n"
            output += f"🕐 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            if include_executive_summary:
                output += "📋 执行摘要\n"
                output += "-" * 30 + "\n"

                revenue = 0
                for key in calculations.keys():
                    if '营业收入' in key and not key.endswith('_ratio'):
                        revenue = calculations[key]
                        break

                food_cost = calculations.get('（二）.食品成本', 0)
                labor_cost = calculations.get('（三）.人工成本', 0)
                investment = calculations.get('九、长期待摄费用_total_investment', 0)

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

            output += "💰 关键财务指标\n"
            output += "-" * 30 + "\n"

            for key, value in list(calculations.items())[:10]:
                if not key.endswith('_ratio') and not key.endswith('_monthly'):
                    output += f"• {key}: ¥{value:,.2f}\n"

            output += "\n📊 财务比率\n"
            output += "-" * 30 + "\n"
            for key, value in calculations.items():
                if key.endswith('_ratio'):
                    output += f"• {key}: {value:.1f}%\n"

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

            if warnings:
                output += "\n⚠️ 注意事项\n"
                output += "-" * 30 + "\n"
                for warning in warnings:
                    output += f"• {warning}\n"

            phases = analysis_result.get('analysis_phases', [])
            if phases:
                output += "\n🔍 分析流程\n"
                output += "-" * 30 + "\n"
                output += f"完成的分析阶段: {' → '.join(phases)}\n"

            if language == "both":
                output += "\n" + "=" * 50 + "\n"
                output += "🏪 Restaurant Financial Analysis Report (Claude Orchestrated)\n"
                output += f"📁 File: {file_path}\n"
                output += f"📅 Report Type: {report_type}\n"
                output += f"📊 Analysis Periods: {', '.join(periods)}\n"
                output += "🤖 Powered by Claude Intelligence (No Hardcoded Rules)\n"
                output += "\n💡 Key Achievement: All analysis driven by Claude's understanding of financial data.\n"

            return self.format_success(output)

        except Exception as e:
            self.logger.error(f"Orchestrated analysis failed: {str(e)}")
            return self.format_error(str(e), "comprehensive_analysis")

    async def handle_adaptive_financial_analysis(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle adaptive financial analysis using AI agents."""
        file_path = arguments.get("file_path")
        analysis_focus = arguments.get("analysis_focus", "comprehensive")
        business_context = arguments.get("business_context")

        if not file_path:
            return self.format_error("file_path is required", "adaptive_financial_analysis")

        if not Path(file_path).exists():
            return self.format_error(f"File not found: {file_path}", "adaptive_financial_analysis")

        try:
            adaptive_analyzer = self.context.get("adaptive_analyzer")
            if not adaptive_analyzer:
                return self.format_error("adaptive_analyzer not available", "adaptive_financial_analysis")

            analysis_prep = await adaptive_analyzer.analyze_excel(
                file_path, analysis_focus, business_context
            )

            if analysis_prep["status"] == "error":
                return self.format_error(analysis_prep['error'], "adaptive_financial_analysis")

            output = f"🤖 智能财务分析 - {Path(file_path).name}\n"
            output += "=" * 60 + "\n"
            output += f"📊 分析重点: {analysis_focus}\n"
            if business_context:
                output += f"🏢 业务背景: {business_context}\n"
            output += f"📁 文件信息: {analysis_prep['file_info']}\n\n"

            output += "🎯 接下来将使用 Claude Code 智能代理进行深度分析...\n"
            output += "该分析将自动适应您的 Excel 格式，无需预定义的模板或映射。\n\n"

            output += "📋 分析提示:\n"
            output += "-" * 30 + "\n"
            output += analysis_prep["analysis_prompt"][:500] + "...\n\n"

            output += "✅ 准备就绪 - 请使用 Claude Code 的 Task 工具完成实际分析\n"

            return self.format_success(output)

        except Exception as e:
            self.logger.error(f"Adaptive analysis failed: {str(e)}")
            return self.format_error(str(e), "adaptive_financial_analysis")

    async def handle_validate_account_structure(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle account structure validation tool call."""
        file_path = arguments.get("file_path")
        show_details = arguments.get("show_details", True)

        if not file_path:
            return self.format_error("file_path is required", "validate_account_structure")

        if not Path(file_path).exists():
            return self.format_error(f"File not found: {file_path}", "validate_account_structure")

        try:
            hierarchy_parser = self.context.get("hierarchy_parser")
            if not hierarchy_parser:
                return self.format_error("hierarchy_parser not available", "validate_account_structure")

            self.logger.info(f"Validating account structure for: {file_path}")

            hierarchy_result = hierarchy_parser.parse_hierarchy(file_path)

            if hierarchy_result.get("parsing_status") != "success":
                error_msg = hierarchy_result.get("error", "Unknown parsing error")
                return self.format_error(error_msg, "validate_account_structure")

            if show_details:
                output = hierarchy_parser.format_hierarchy_display(hierarchy_result)
            else:
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

            output += "\n\n🔒 VALIDATION CHECKPOINT\n"
            output += "=" * 40 + "\n"
            output += "Before proceeding with any calculations:\n"
            output += "✅ Confirm account structure is correct\n"
            output += "✅ Specify depreciation/amortization periods\n"
            output += "✅ Choose which accounts to use for calculations\n"
            output += "✅ Document all assumptions for audit trail\n\n"

            output += "💡 TIP: Only proceed with financial analysis after user confirms all assumptions!\n"

            self.logger.info(f"Account structure validation completed for {file_path}")
            return self.format_success(output)

        except Exception as e:
            self.logger.error(f"Account structure validation failed: {str(e)}")
            return self.format_error(str(e), "validate_account_structure")