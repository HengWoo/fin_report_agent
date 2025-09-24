"""
Thinking Handler

Handles metacognitive reflection and analysis validation tools.
"""

from typing import Dict, Any
from mcp.types import TextContent
from .base import BaseHandler
from ..thinking_tools import thinking_tools


class ThinkingHandler(BaseHandler):
    """Handler for thinking and reflection tools."""

    async def handle_think_about_financial_data(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle think_about_financial_data tool call."""
        collected_data = arguments.get("collected_data", {})
        analysis_goal = arguments.get("analysis_goal", "")

        try:
            result = thinking_tools.think_about_financial_data(
                collected_data, analysis_goal
            )

            output = f"🤔 Reflection: Financial Data Assessment\n"
            output += "=" * 50 + "\n\n"
            output += f"**Summary:** {result.summary}\n"
            output += f"**Confidence:** {result.confidence * 100:.0f}%\n\n"

            output += f"**Analysis Goal:** {analysis_goal}\n\n"

            if result.recommendations:
                output += "**Recommendations:**\n"
                for rec in result.recommendations:
                    output += f"  {rec}\n"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "think_about_financial_data")

    async def handle_think_about_analysis_completeness(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle think_about_analysis_completeness tool call."""
        analysis_performed = arguments.get("analysis_performed", [])
        required_components = arguments.get("required_components", [])

        try:
            result = thinking_tools.think_about_analysis_completeness(
                analysis_performed, required_components
            )

            output = f"✅ Analysis Completeness Check\n"
            output += "=" * 50 + "\n\n"
            output += f"**Summary:** {result.summary}\n"
            output += f"**Completion Rate:** {result.confidence * 100:.0f}%\n\n"

            details = result.details
            output += f"**Completed:** {details['completed_count']}/{details['total_required']}\n"

            if details.get("completed"):
                output += f"\n**✅ Completed Components:**\n"
                for comp in details["completed"]:
                    output += f"  ✓ {comp}\n"

            if details.get("missing"):
                output += f"\n**❌ Missing Components:**\n"
                for comp in details["missing"]:
                    output += f"  ✗ {comp}\n"

            if result.recommendations:
                output += f"\n**Next Steps:**\n"
                for rec in result.recommendations:
                    output += f"  {rec}\n"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "think_about_analysis_completeness")

    async def handle_think_about_assumptions(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle think_about_assumptions tool call."""
        assumptions = arguments.get("assumptions", {})
        financial_context = arguments.get("financial_context", {})

        try:
            result = thinking_tools.think_about_assumptions(
                assumptions, financial_context
            )

            output = f"🔍 Assumption Validation\n"
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
                output += f"\n**Recommendations:**\n"
                for rec in result.recommendations:
                    output += f"  {rec}\n"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "think_about_assumptions")