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
