"""
Memory Handler

Handles session memory, insights, and knowledge persistence tools.
"""

from typing import Dict, Any
from mcp.types import TextContent
from .base import BaseHandler
from ..financial_memory import financial_memory_manager


class MemoryHandler(BaseHandler):
    """Handler for memory and session management tools."""

    async def handle_save_analysis_insight(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle save_analysis_insight tool call."""
        session_id = arguments.get("session_id")
        key = arguments.get("key")
        description = arguments.get("description")
        insight_type = arguments.get("insight_type")
        context = arguments.get("context", {})
        confidence = arguments.get("confidence", 0.8)

        try:
            success = financial_memory_manager.save_insight(
                session_id, key, description, insight_type, context, confidence
            )

            if success:
                output = "💾 Insight Saved Successfully\n"
                output += "=" * 50 + "\n\n"
                output += f"**Key:** {key}\n"
                output += f"**Type:** {insight_type}\n"
                output += f"**Description:** {description}\n"
                output += f"**Confidence:** {confidence * 100:.0f}%\n"
                output += f"**Session:** {session_id}\n"
            else:
                output = f"❌ Failed to save insight (session not found: {session_id})"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "save_analysis_insight")

    async def handle_get_session_context(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle get_session_context tool call."""
        session_id = arguments.get("session_id")

        try:
            context = financial_memory_manager.get_context_summary(session_id)

            if "error" in context:
                return self.format_error(context["error"], "get_session_context")

            output = "📋 Session Context Summary\n"
            output += "=" * 50 + "\n\n"
            output += f"**Session ID:** {context['session_id']}\n"
            output += f"**File:** {context['file_path']}\n"
            output += f"**Created:** {context['created_at']}\n"
            output += f"**Last Accessed:** {context['last_accessed']}\n\n"

            output += "**Statistics:**\n"
            output += f"  • Insights: {context['insights_count']}\n"
            output += f"  • Patterns: {context['patterns_count']}\n"
            output += f"  • History Events: {context['history_count']}\n"
            output += f"  • Questions Asked: {context['questions_asked_count']}\n\n"

            if context.get("recent_insights"):
                output += "**Recent Insights:**\n"
                for insight in context["recent_insights"]:
                    output += (
                        f"  • [{insight['insight_type']}] {insight['description']}\n"
                    )

            if context.get("user_preferences"):
                output += (
                    f"\n**User Preferences:** {len(context['user_preferences'])} set\n"
                )

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "get_session_context")

    async def handle_write_memory_note(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle write_memory_note tool call."""
        name = arguments.get("name")
        content = arguments.get("content")
        session_id = arguments.get("session_id")

        try:
            success = financial_memory_manager.write_memory_file(
                name, content, session_id
            )

            if success:
                output = "📝 Memory Note Saved\n"
                output += "=" * 50 + "\n\n"
                output += f"**Name:** {name}.md\n"
                if session_id:
                    output += f"**Session:** {session_id}\n"
                output += "\n**Content Preview:**\n"
                output += content[:200] + ("..." if len(content) > 200 else "")
            else:
                output = "❌ Failed to save memory note"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "write_memory_note")
