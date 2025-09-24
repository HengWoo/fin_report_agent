"""
Navigation Handler

Handles LSP-like financial account navigation and structure exploration.
"""

from typing import Dict, Any
from mcp.types import TextContent
from .base import BaseHandler
from ..financial_navigator import financial_navigator


class NavigationHandler(BaseHandler):
    """Handler for LSP-like account navigation tools."""

    async def handle_find_account(self, arguments: Dict[str, Any]) -> TextContent:
        """Handle find_account tool call."""
        file_path = arguments.get("file_path")
        name_pattern = arguments.get("name_pattern")
        exact_match = arguments.get("exact_match", False)
        account_type = arguments.get("account_type")

        try:
            accounts = financial_navigator.find_account(
                file_path, name_pattern, exact_match, account_type
            )

            output = f"🔍 Found {len(accounts)} account(s) matching '{name_pattern}'\n"
            output += "=" * 50 + "\n\n"

            for account in accounts[:10]:  # Limit to 10
                output += f"📌 {account.name}\n"
                output += f"   Path: {account.name_path}\n"
                output += f"   Type: {account.account_type}\n"
                output += f"   Level: {account.level}\n"
                if account.values:
                    output += f"   Values: {account.values}\n"
                output += f"   {'🍃 Leaf' if account.is_leaf() else '📂 Has children'}\n\n"

            if len(accounts) > 10:
                output += f"... and {len(accounts) - 10} more accounts\n"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "find_account")

    async def handle_get_financial_overview(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle get_financial_overview tool call."""
        file_path = arguments.get("file_path")
        max_depth = arguments.get("max_depth", 2)

        try:
            overview = financial_navigator.get_financial_overview(file_path, max_depth)

            output = f"📊 Financial Structure Overview (depth ≤ {max_depth})\n"
            output += "=" * 50 + "\n\n"

            current_level = -1
            for account in overview:
                if account.level != current_level:
                    current_level = account.level
                    output += f"\n{'━' * 40}\n"
                    output += f"Level {current_level}\n"
                    output += f"{'━' * 40}\n\n"

                indent = "  " * account.level
                icon = "🍃" if account.is_leaf() else "📂"
                output += f"{indent}{icon} {account.name} ({account.account_type})\n"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "get_financial_overview")

    async def handle_get_account_context(
        self, arguments: Dict[str, Any]
    ) -> TextContent:
        """Handle get_account_context tool call."""
        file_path = arguments.get("file_path")
        account_name_path = arguments.get("account_name_path")
        depth = arguments.get("depth", 1)

        try:
            context = financial_navigator.get_account_context(
                file_path, account_name_path, depth
            )

            if "error" in context:
                return self.format_error(context["error"], "get_account_context")

            account = context["account"]
            output = f"📍 Account Context: {account['name']}\n"
            output += "=" * 50 + "\n\n"

            output += f"**Account Details:**\n"
            output += f"  Path: {account['name_path']}\n"
            output += f"  Type: {account['account_type']}\n"
            output += f"  Level: {account['level']}\n"
            output += f"  Status: {'🍃 Leaf' if account['is_leaf'] else '📂 Parent'}\n\n"

            if context.get("ancestors"):
                output += f"**Ancestors (path from root):**\n"
                for anc in reversed(context["ancestors"]):
                    output += f"  └─ {anc['name']}\n"
                output += "\n"

            if context.get("children"):
                output += f"**Children ({len(context['children'])}):**\n"
                for child in context["children"][:5]:
                    output += f"  ├─ {child['name']} ({child['account_type']})\n"
                if len(context["children"]) > 5:
                    output += (
                        f"  └─ ... and {len(context['children']) - 5} more\n"
                    )
                output += "\n"

            if context.get("siblings"):
                output += f"**Siblings ({len(context['siblings'])}):**\n"
                for sib in context["siblings"][:3]:
                    output += f"  • {sib['name']}\n"
                if len(context["siblings"]) > 3:
                    output += f"  • ... and {len(context['siblings']) - 3} more\n"

            return self.format_success(output)
        except Exception as e:
            return self.format_error(str(e), "get_account_context")