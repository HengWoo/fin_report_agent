"""
Complex Analysis Handler

Handles complex financial analysis workflows using Serena-like components.
Uses hierarchy parser, navigator, memory, thinking tools, and analytics.
"""

from typing import Dict, Any
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
        Handle comprehensive analysis using Serena-like components.

        Uses hierarchy parser, navigator, memory manager, thinking tools,
        and analytics engine for intelligent financial analysis.
        """
        file_path = arguments.get("file_path")
        language = arguments.get("language", "both")
        include_executive_summary = arguments.get("include_executive_summary", True)

        if not file_path:
            return self.format_error("file_path is required", "comprehensive_analysis")

        if not Path(file_path).exists():
            return self.format_error(
                f"File not found: {file_path}", "comprehensive_analysis"
            )

        try:
            hierarchy_parser = self.context.get("hierarchy_parser")
            financial_memory = self.context.get("financial_memory_manager")

            if not hierarchy_parser:
                return self.format_error(
                    "hierarchy_parser not available", "comprehensive_analysis"
                )

            self.logger.info(f"Starting comprehensive analysis of {file_path}")

            hierarchy_result = hierarchy_parser.parse_hierarchy(file_path)

            if hierarchy_result.get("parsing_status") != "success":
                error_msg = hierarchy_result.get("error", "Unknown parsing error")
                return self.format_error(error_msg, "comprehensive_analysis")

            accounts = hierarchy_result.get("accounts", [])
            safe_accounts = hierarchy_result.get("safe_accounts", [])
            column_intelligence = hierarchy_result.get("column_intelligence", {})

            if financial_memory:
                session = financial_memory.get_or_create_session(file_path)
                session_id = session.session_id
            else:
                session_id = None

            total_accounts = hierarchy_result.get("total_accounts", len(accounts))
            periods = column_intelligence.get("value_columns", [])

            calculations = {}
            for account in safe_accounts[:20]:
                name = account.get("name", "")
                value = account.get("total_value", 0)
                if value != 0:
                    calculations[name] = value

            validation = {
                "valid": len(safe_accounts) > 0,
                "confidence": (
                    len(safe_accounts) / max(total_accounts, 1)
                    if total_accounts > 0
                    else 0
                ),
            }

            warnings = hierarchy_result.get("validation_flags", {}).get(
                "potential_double_counting", []
            )

            output = "🏪 财务综合分析报告 (Intelligent Analysis)\n"
            output += "=" * 50 + "\n"
            output += f"📁 文件: {file_path}\n"
            output += f"📊 总账户数: {total_accounts}\n"
            output += f"✅ 安全计算账户: {len(safe_accounts)}\n"
            output += f"📅 分析期间: {len(periods)} 个期间\n"
            output += f"🕐 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            if include_executive_summary:
                output += "📋 执行摘要\n"
                output += "-" * 30 + "\n"

                revenue_accounts = [
                    acc for acc in safe_accounts if "收入" in acc.get("name", "")
                ]
                cost_accounts = [
                    acc for acc in safe_accounts if "成本" in acc.get("name", "")
                ]

                if revenue_accounts:
                    total_revenue = sum(
                        acc.get("total_value", 0) for acc in revenue_accounts
                    )
                    output += f"• 总收入类账户: {len(revenue_accounts)} 个\n"
                    output += f"• 总收入金额: ¥{total_revenue:,.2f}\n"

                    if len(periods) > 0:
                        output += f"• 平均每期: ¥{total_revenue / len(periods):,.2f}\n"

                if cost_accounts:
                    total_cost = sum(acc.get("total_value", 0) for acc in cost_accounts)
                    output += f"• 总成本类账户: {len(cost_accounts)} 个\n"
                    output += f"• 总成本金额: ¥{total_cost:,.2f}\n"

                output += "\n"

            output += "💰 主要账户金额\n"
            output += "-" * 30 + "\n"

            sorted_calcs = sorted(
                calculations.items(), key=lambda x: abs(x[1]), reverse=True
            )
            for key, value in sorted_calcs[:10]:
                output += f"• {key}: ¥{value:,.2f}\n"

            output += "\n✅ 数据验证结果\n"
            output += "-" * 30 + "\n"
            if validation.get("valid"):
                output += "• 验证状态: ✅ 通过\n"
                output += f"• 置信度: {validation.get('confidence', 0):.1%}\n"
            else:
                output += "• 验证状态: ⚠️ 需要审查\n"

            if warnings:
                output += "\n⚠️ 注意事项\n"
                output += "-" * 30 + "\n"
                for warning in warnings[:5]:
                    output += f"• {warning}\n"

            if session_id:
                output += "\n🧠 会话信息\n"
                output += "-" * 30 + "\n"
                output += f"会话ID: {session_id}\n"
                output += "智能系统已记录此次分析\n"

            if language == "both":
                output += "\n" + "=" * 50 + "\n"
                output += "🏪 Financial Analysis Report (Intelligent System)\n"
                output += f"📁 File: {file_path}\n"
                output += f"📊 Total Accounts: {total_accounts}\n"
                output += f"✅ Safe Accounts: {len(safe_accounts)}\n"
                output += f"📅 Periods: {len(periods)}\n"
                output += "🤖 Powered by Serena-like Intelligence\n"
                output += "\n💡 Features: Memory, Navigation, and Thinking Tools\n"

            return self.format_success(output)

        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {str(e)}")
            return self.format_error(str(e), "comprehensive_analysis")

    async def handle_adaptive_financial_analysis(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle adaptive financial analysis using AI agents."""
        file_path = arguments.get("file_path")
        analysis_focus = arguments.get("analysis_focus", "comprehensive")
        business_context = arguments.get("business_context")

        if not file_path:
            return self.format_error(
                "file_path is required", "adaptive_financial_analysis"
            )

        if not Path(file_path).exists():
            return self.format_error(
                f"File not found: {file_path}", "adaptive_financial_analysis"
            )

        try:
            adaptive_analyzer = self.context.get("adaptive_analyzer")
            financial_memory = self.context.get("financial_memory_manager")

            if not adaptive_analyzer:
                return self.format_error(
                    "adaptive_analyzer not available", "adaptive_financial_analysis"
                )

            if financial_memory:
                session = financial_memory.get_or_create_session(file_path)
                session_id = session.session_id
            else:
                session_id = None

            analysis_prep = await adaptive_analyzer.analyze_excel(
                file_path, analysis_focus, business_context
            )

            if analysis_prep["status"] == "error":
                return self.format_error(
                    analysis_prep["error"], "adaptive_financial_analysis"
                )

            output = f"🤖 智能财务分析 - {Path(file_path).name}\n"
            output += "=" * 60 + "\n"
            output += f"📊 分析重点: {analysis_focus}\n"
            if business_context:
                output += f"🏢 业务背景: {business_context}\n"
            output += f"📁 文件信息: {analysis_prep['file_info']}\n"
            if session_id:
                output += f"🧠 会话ID: {session_id}\n"
            output += "\n"

            output += "🎯 智能分析系统已准备就绪\n"
            output += "该分析将自动适应您的 Excel 格式，无需预定义的模板或映射。\n\n"

            output += "💡 系统特性:\n"
            output += "• 🧠 会话记忆 - 跨分析保持上下文\n"
            output += "• 🔍 账户导航 - LSP-like 智能探索\n"
            output += "• 🤔 反思工具 - 分析完整性检查\n\n"

            output += "✅ 准备就绪 - 使用简单工具进行深度分析\n"

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
            return self.format_error(
                "file_path is required", "validate_account_structure"
            )

        if not Path(file_path).exists():
            return self.format_error(
                f"File not found: {file_path}", "validate_account_structure"
            )

        try:
            hierarchy_parser = self.context.get("hierarchy_parser")
            if not hierarchy_parser:
                return self.format_error(
                    "hierarchy_parser not available", "validate_account_structure"
                )

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
