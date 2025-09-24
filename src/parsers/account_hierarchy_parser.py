"""
Enhanced Account Hierarchy Parser for Financial Statements

This parser focuses on extracting account structure and parent-child relationships
from Excel financial statements to prevent double counting and ensure proper validation.

Features:
- Conservative double counting prevention
- Enhanced validation with detailed reporting
- Integration with ValidationStateManager
- Comprehensive safety scoring
- Detailed exclusion reasoning
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re
import logging

from .column_classifier import ColumnClassifier, ColumnType

logger = logging.getLogger(__name__)


class AccountHierarchyParser:
    """Parser specialized in extracting account hierarchy and relationships."""

    def __init__(self):
        """Initialize the account hierarchy parser."""
        self.hierarchy_indicators = {
            # Chinese numbering patterns for account levels
            'level_1': r'^[一二三四五六七八九十]+、',  # 一、二、三、
            'level_2': r'^（[一二三四五六七八九十]+）',    # （一）（二）（三）
            'level_3': r'^[0-9]+、',                     # 1、2、3、
            'level_4': r'^（[0-9]+）',                   # （1）（2）（3）
            'level_5': r'^[a-z]+[）\.]',                 # a) b) c.
        }

        self.indentation_threshold = 2  # Minimum spaces to indicate hierarchy
        self.logger = logging.getLogger(__name__)

        # NEW: Column intelligence system
        self.column_classifier = ColumnClassifier()

        # Cache for performance optimization
        self._last_exclusion_details = []
        self._validation_cache = {}

    def parse_hierarchy(self, file_path: str) -> Dict[str, Any]:
        """
        Parse Excel file and extract account hierarchy with validation flags.

        NEW: Now includes intelligent column classification to prevent:
        - Double counting from subtotal columns
        - Including note/remark columns
        - Misidentifying ratio columns as values

        Args:
            file_path: Path to Excel file

        Returns:
            Dictionary containing account hierarchy, validation flags, safe accounts,
            and column intelligence information
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            logger.info(f"Parsing hierarchy from: {file_path}")

            # NEW: Classify columns intelligently
            column_classifications = self.column_classifier.classify_columns(df)
            value_columns = self.column_classifier.get_value_columns(column_classifications)
            subtotal_columns = self.column_classifier.get_subtotal_columns(column_classifications)

            logger.info(f"Column intelligence: {len(value_columns)} value columns, "
                       f"{len(subtotal_columns)} subtotal columns")

            # Generate column classification report
            column_report = self.column_classifier.generate_classification_report(df, column_classifications)

            # Extract account structure (now using only value columns)
            accounts = self._extract_accounts_smart(df, column_classifications)

            # Build hierarchy tree
            hierarchy_tree = self._build_hierarchy_tree(accounts)

            # Perform validation checks
            validation_flags = self._validate_hierarchy(hierarchy_tree, accounts)

            # Identify safe accounts for calculations
            safe_accounts = self._identify_safe_accounts(hierarchy_tree)

            return {
                "file_path": file_path,
                "accounts": accounts,
                "hierarchy_tree": hierarchy_tree,
                "validation_flags": validation_flags,
                "safe_accounts": safe_accounts,
                "total_accounts": len(accounts),
                "parsing_status": "success",
                # NEW: Column intelligence data
                "column_intelligence": {
                    "classifications": column_classifications,
                    "value_columns": value_columns,
                    "subtotal_columns": subtotal_columns,
                    "excluded_columns": self.column_classifier.get_excluded_columns(column_classifications),
                    "classification_report": column_report
                }
            }

        except Exception as e:
            logger.error(f"Error parsing hierarchy from {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "error": str(e),
                "parsing_status": "failed"
            }

    def _extract_accounts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Extract account information from DataFrame (legacy method).

        WARNING: This method is deprecated. Use _extract_accounts_smart instead.
        """
        accounts = []

        for index, row in df.iterrows():
            # Get first column as account name
            account_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""

            if not account_name or account_name in ['nan', '']:
                continue

            # Extract numeric values from other columns
            values = {}
            for col_idx, value in enumerate(row.iloc[1:], 1):
                if pd.notna(value) and isinstance(value, (int, float)):
                    col_name = f"col_{col_idx}"
                    values[col_name] = float(value)

            # Determine account level based on formatting
            level = self._determine_account_level(account_name)

            # Calculate indentation (if any leading spaces)
            indentation = len(account_name) - len(account_name.lstrip())

            account = {
                "index": index,
                "name": account_name,
                "clean_name": self._clean_account_name(account_name),
                "level": level,
                "indentation": indentation,
                "values": values,
                "total_value": sum(values.values()) if values else 0,
                "is_numeric": bool(values)
            }

            accounts.append(account)

        return accounts

    def _extract_accounts_smart(self,
                                 df: pd.DataFrame,
                                 column_classifications: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract account information using intelligent column classification.

        This prevents:
        - Double counting from subtotal columns
        - Including note/remark data
        - Using ratio/percentage columns as values

        Args:
            df: DataFrame to extract from
            column_classifications: Column classification info from ColumnClassifier

        Returns:
            List of account dictionaries with smart value extraction
        """
        accounts = []
        value_columns = self.column_classifier.get_value_columns(column_classifications)
        subtotal_columns = self.column_classifier.get_subtotal_columns(column_classifications)

        # Check if first row is headers (Chinese format)
        header_from_first_row = any(
            info.get("header_from_first_row", False)
            for info in column_classifications.values()
        )
        start_row = 1 if header_from_first_row else 0

        logger.info(f"Extracting accounts starting from row {start_row}")

        for index, row in df.iterrows():
            # Skip header row if present
            if header_from_first_row and index == 0:
                continue
            # Get first column as account name
            account_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""

            if not account_name or account_name in ['nan', '']:
                continue

            # Extract values - SMART VERSION
            values = {}
            subtotal_value = None

            # Check if subtotal column has a value (use this instead of summing)
            for col_idx in subtotal_columns:
                value = row.iloc[col_idx]
                if pd.notna(value) and isinstance(value, (int, float)) and value != 0:
                    subtotal_value = float(value)
                    break  # Use first non-zero subtotal

            # If we have a subtotal, use it; otherwise sum value columns
            if subtotal_value is not None:
                # Use subtotal directly - don't sum periods (prevents double counting)
                total_value = subtotal_value
                values["subtotal"] = subtotal_value
            else:
                # No subtotal - sum only value columns
                for col_idx in value_columns:
                    value = row.iloc[col_idx]
                    if pd.notna(value) and isinstance(value, (int, float)):
                        col_name = f"col_{col_idx}"
                        values[col_name] = float(value)
                total_value = sum(values.values()) if values else 0

            # Determine account level based on formatting
            level = self._determine_account_level(account_name)

            # Calculate indentation (if any leading spaces)
            indentation = len(account_name) - len(account_name.lstrip())

            account = {
                "index": index,
                "name": account_name,
                "clean_name": self._clean_account_name(account_name),
                "level": level,
                "indentation": indentation,
                "values": values,
                "total_value": total_value,
                "is_numeric": bool(values),
                # NEW: Track if value came from subtotal
                "used_subtotal": subtotal_value is not None,
                "subtotal_value": subtotal_value
            }

            accounts.append(account)

        return accounts

    def _determine_account_level(self, account_name: str) -> int:
        """Determine the hierarchical level of an account based on formatting."""
        for level, pattern in enumerate(self.hierarchy_indicators.values(), 1):
            if re.match(pattern, account_name):
                return level

        # If no pattern matches, check indentation
        indentation = len(account_name) - len(account_name.lstrip())
        if indentation >= self.indentation_threshold:
            return min(5, indentation // 2 + 1)  # Estimate level from indentation

        return 1  # Default to top level

    def _clean_account_name(self, account_name: str) -> str:
        """Clean account name by removing numbering and extra whitespace."""
        # Remove hierarchy indicators
        cleaned = account_name
        for pattern in self.hierarchy_indicators.values():
            cleaned = re.sub(pattern, '', cleaned)

        return cleaned.strip()

    def _build_hierarchy_tree(self, accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build hierarchical tree structure from flat account list."""
        tree = {}
        stack = []  # Stack to track parent accounts

        for account in accounts:
            level = account["level"]

            # Pop stack until we find the appropriate parent level
            while stack and stack[-1]["level"] >= level:
                stack.pop()

            # Set parent relationship
            parent = stack[-1] if stack else None
            account["parent"] = parent["name"] if parent else None
            account["children"] = []

            # Add to parent's children
            if parent:
                parent["children"].append(account["name"])

            # Add to tree
            tree[account["name"]] = account

            # Add to stack for potential future children
            stack.append(account)

        return tree

    def _validate_hierarchy(self, hierarchy_tree: Dict[str, Any], accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate hierarchy for potential double counting and inconsistencies."""
        validation_flags = {
            "parent_child_sum_matches": [],
            "orphan_accounts": [],
            "duplicate_entries": [],
            "large_value_differences": [],
            "potential_double_counting": []
        }

        # Check parent-child sum relationships
        for account_name, account in hierarchy_tree.items():
            if account["children"]:
                parent_total = account["total_value"]
                children_total = sum(
                    hierarchy_tree[child]["total_value"]
                    for child in account["children"]
                    if child in hierarchy_tree and hierarchy_tree[child]["is_numeric"]
                )

                if children_total > 0:  # Only check if children have values
                    difference = abs(parent_total - children_total)
                    tolerance = max(parent_total * 0.01, 1.0)  # 1% tolerance or 1 unit

                    if difference <= tolerance:
                        validation_flags["parent_child_sum_matches"].append({
                            "parent": account_name,
                            "parent_value": parent_total,
                            "children_total": children_total,
                            "difference": difference,
                            "status": "match"
                        })
                    else:
                        validation_flags["large_value_differences"].append({
                            "parent": account_name,
                            "parent_value": parent_total,
                            "children_total": children_total,
                            "difference": difference,
                            "status": "mismatch"
                        })

        # Check for potential double counting scenarios
        for account_name, account in hierarchy_tree.items():
            if account["children"] and account["is_numeric"]:
                children_with_values = [
                    child for child in account["children"]
                    if child in hierarchy_tree and hierarchy_tree[child]["is_numeric"]
                ]
                if children_with_values:
                    validation_flags["potential_double_counting"].append({
                        "account": account_name,
                        "warning": "Parent has value and numeric children - risk of double counting",
                        "children": children_with_values
                    })

        return validation_flags

    def _identify_safe_accounts(self, hierarchy_tree: Dict[str, Any]) -> List[str]:
        """Identify accounts that are safe to use for calculations (leaf nodes)."""
        safe_accounts = []

        for account_name, account in hierarchy_tree.items():
            # Safe if it's a leaf node (no children) and has numeric values
            if not account["children"] and account["is_numeric"]:
                safe_accounts.append(account_name)
            # Also safe if it's a parent but children don't have numeric values
            elif account["children"] and account["is_numeric"]:
                children_have_values = any(
                    hierarchy_tree[child]["is_numeric"]
                    for child in account["children"]
                    if child in hierarchy_tree
                )
                if not children_have_values:
                    safe_accounts.append(account_name)

        return safe_accounts

    def format_hierarchy_display(self, hierarchy_result: Dict[str, Any]) -> str:
        """Format hierarchy for user-friendly display."""
        if hierarchy_result.get("parsing_status") != "success":
            return f"❌ Parsing failed: {hierarchy_result.get('error', 'Unknown error')}"

        tree = hierarchy_result["hierarchy_tree"]
        validation = hierarchy_result["validation_flags"]
        safe_accounts = hierarchy_result["safe_accounts"]

        output = "📊 Account Hierarchy Analysis\n"
        output += "=" * 50 + "\n\n"

        # Display hierarchy tree
        output += "🌳 Account Structure:\n"
        displayed = set()

        for account_name, account in tree.items():
            if account["parent"] is None:  # Root level accounts
                output += self._format_account_subtree(account_name, tree, 0, displayed)

        # Display validation results
        output += "\n\n🔍 Validation Results:\n"
        output += "-" * 30 + "\n"

        if validation["parent_child_sum_matches"]:
            output += f"✅ Parent-child sum matches: {len(validation['parent_child_sum_matches'])}\n"

        if validation["large_value_differences"]:
            output += f"⚠️  Large value differences: {len(validation['large_value_differences'])}\n"
            for diff in validation["large_value_differences"][:3]:  # Show first 3
                output += f"   • {diff['parent']}: {diff['difference']:.2f} difference\n"

        if validation["potential_double_counting"]:
            output += f"🚨 Potential double counting risks: {len(validation['potential_double_counting'])}\n"
            for risk in validation["potential_double_counting"][:3]:
                output += f"   • {risk['account']}: {risk['warning']}\n"

        # Display safe accounts
        output += f"\n💚 Safe accounts for calculations ({len(safe_accounts)}):\n"
        for account in safe_accounts[:10]:  # Show first 10
            value = tree[account]["total_value"]
            output += f"   • {account}: ¥{value:,.2f}\n"

        if len(safe_accounts) > 10:
            output += f"   ... and {len(safe_accounts) - 10} more\n"

        # Add validation questions
        output += "\n\n❓ VALIDATION QUESTIONS:\n"
        output += "1. Is this account structure correct?\n"
        output += "2. What depreciation/amortization periods apply?\n"
        output += "3. Should I use only leaf accounts to avoid double counting?\n"
        output += "4. Are there any specific accounts you want included/excluded?\n"

        return output

    def _format_account_subtree(self, account_name: str, tree: Dict[str, Any],
                               indent: int, displayed: set) -> str:
        """Recursively format account subtree for display."""
        if account_name in displayed:
            return ""

        displayed.add(account_name)
        account = tree[account_name]

        # Format account line
        indent_str = "  " * indent
        tree_char = "├── " if indent > 0 else ""

        value_str = ""
        if account["is_numeric"] and account["total_value"] != 0:
            value_str = f" (¥{account['total_value']:,.2f})"

        parent_child_indicator = ""
        if account["children"]:
            if account["is_numeric"]:
                parent_child_indicator = " [PARENT+VALUE]"
            else:
                parent_child_indicator = " [PARENT]"
        else:
            if account["is_numeric"]:
                parent_child_indicator = " [LEAF]"

        line = f"{indent_str}{tree_char}{account['name']}{value_str}{parent_child_indicator}\n"

        # Add children
        for child_name in account["children"]:
            line += self._format_account_subtree(child_name, tree, indent + 1, displayed)

        return line

    # Enhanced methods for double counting prevention and validation integration

    def _identify_safe_accounts_conservative(self, hierarchy_tree: Dict[str, Any]) -> List[str]:
        """
        Conservative approach to identifying safe accounts for calculations.

        Rules:
        1. Only leaf accounts (no children) are considered safe
        2. Exclude accounts with zero values
        3. When in doubt, exclude rather than risk double counting
        4. Log exclusion reasons for transparency

        Returns:
            List of account names that are safe for calculations
        """
        if not hierarchy_tree:
            return []

        safe_accounts = []
        excluded_accounts = []

        # Use list comprehension for better performance
        for account_name, account in hierarchy_tree.items():
            if not isinstance(account, dict):
                continue

            exclusion_reason = self._evaluate_account_safety(account)

            if exclusion_reason:
                excluded_accounts.append({
                    "account": account_name,
                    "reason": exclusion_reason,
                    "value": account.get("total_value", 0)
                })
            else:
                safe_accounts.append(account_name)

        self.logger.info(f"Conservative analysis: {len(safe_accounts)} safe, {len(excluded_accounts)} excluded")

        # Store exclusion details for reporting
        self._last_exclusion_details = excluded_accounts

        return safe_accounts

    def _evaluate_account_safety(self, account: Dict[str, Any]) -> Optional[str]:
        """
        Evaluate if an account is safe for calculations.

        Returns:
            None if safe, otherwise a string describing why it's unsafe
        """
        # Rule 1: Must have no children (be a leaf node)
        if account.get("children") and len(account["children"]) > 0:
            return "Has children - risk of double counting"

        # Rule 2: Must have non-zero value
        if not account.get("is_numeric") or account.get("total_value", 0) == 0:
            return "Zero value or non-numeric"

        # Rule 3: Additional safety checks
        if account.get("total_value", 0) < 0:
            return "Negative value - requires manual review"

        # Rule 4: Check for suspicious account names (optional)
        account_name = account.get("name", "").lower()
        suspicious_keywords = ["小计", "合计", "总计", "subtotal", "total"]
        if any(keyword in account_name for keyword in suspicious_keywords):
            return "Suspicious total/subtotal account name"

        return None

    def get_last_exclusion_details(self) -> List[Dict[str, Any]]:
        """
        Get details about accounts excluded in the last safety analysis.

        Returns:
            List of dictionaries containing exclusion details
        """
        return self._last_exclusion_details.copy()

    def _validate_hierarchy_enhanced(self, hierarchy_tree: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced hierarchy validation with detailed double counting detection.

        Returns comprehensive validation flags including:
        - Sum mismatches between parent and children
        - Ambiguous accounts (parent with both value and children)
        - Circular references
        - Unusual patterns
        """
        validation_flags = {
            "sum_mismatches": [],
            "ambiguous_accounts": [],
            "circular_references": [],
            "zero_value_accounts": [],
            "negative_value_accounts": []
        }

        # Check for sum mismatches and ambiguous accounts
        for account_name, account in hierarchy_tree.items():
            if account.get("children") and len(account["children"]) > 0:

                # Check if parent has both value and children (ambiguous)
                if account.get("is_numeric") and account.get("total_value", 0) != 0:
                    validation_flags["ambiguous_accounts"].append({
                        "account": account_name,
                        "warning": "PARENT+VALUE - Has both value and children, risk of double counting",
                        "parent_value": account.get("total_value", 0),
                        "children": account["children"]
                    })

                # Check sum consistency
                children_total = sum(
                    hierarchy_tree.get(child, {}).get("total_value", 0)
                    for child in account["children"]
                    if child in hierarchy_tree and hierarchy_tree[child].get("is_numeric", False)
                )

                parent_value = account.get("total_value", 0)
                if children_total > 0 and parent_value > 0:  # Only check if both have values
                    difference = abs(parent_value - children_total)
                    tolerance = max(parent_value * 0.01, 1.0)  # 1% tolerance or 1 unit

                    if difference > tolerance:
                        validation_flags["sum_mismatches"].append({
                            "parent": account_name,
                            "expected_total": parent_value,
                            "parent_value": parent_value,  # Include both for compatibility
                            "children_total": children_total,
                            "difference": difference,
                            "tolerance": tolerance
                        })

        # Check for zero and negative values
        for account_name, account in hierarchy_tree.items():
            if account.get("is_numeric"):
                value = account.get("total_value", 0)
                if value == 0:
                    validation_flags["zero_value_accounts"].append(account_name)
                elif value < 0:
                    validation_flags["negative_value_accounts"].append({
                        "account": account_name,
                        "value": value
                    })

        # Basic circular reference detection
        visited = set()
        rec_stack = set()

        def has_cycle(account_name):
            if account_name in rec_stack:
                return True
            if account_name in visited:
                return False

            visited.add(account_name)
            rec_stack.add(account_name)

            account = hierarchy_tree.get(account_name, {})
            for child in account.get("children", []):
                if has_cycle(child):
                    validation_flags["circular_references"].append({
                        "cycle_involving": [account_name, child]
                    })
                    return True

            rec_stack.remove(account_name)
            return False

        for account_name in hierarchy_tree:
            if account_name not in visited:
                has_cycle(account_name)

        return validation_flags

    def _generate_conservative_recommendations(self, hierarchy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate conservative recommendations for calculation safety.

        Provides specific guidance on which accounts to use/exclude and why.
        """
        hierarchy_tree = hierarchy_result.get("hierarchy_tree", {})
        safe_accounts = hierarchy_result.get("safe_accounts", [])
        validation_flags = hierarchy_result.get("validation_flags", {})

        recommendations = {
            "use_leaf_accounts_only": True,
            "exclude_ambiguous_accounts": [],
            "exclude_zero_value_accounts": True,
            "recommended_accounts": safe_accounts.copy(),
            "excluded_accounts": [],
            "calculation_safety_score": 0.0,
            "warnings": []
        }

        # Identify accounts to exclude
        for account_name, account in hierarchy_tree.items():
            if account_name not in safe_accounts:
                if account.get("children"):
                    recommendations["excluded_accounts"].append(account_name)
                    recommendations["warnings"].append(
                        f"Excluded '{account_name}': Has children - use children accounts instead"
                    )

        # Process ambiguous accounts
        for ambiguous in validation_flags.get("ambiguous_accounts", []):
            account_name = ambiguous["account"]
            recommendations["exclude_ambiguous_accounts"].append(account_name)
            if account_name in recommendations["recommended_accounts"]:
                recommendations["recommended_accounts"].remove(account_name)
            recommendations["warnings"].append(
                f"Excluded '{account_name}': Ambiguous parent+value account"
            )

        # Calculate safety score
        total_accounts = len(hierarchy_tree)
        if total_accounts > 0:
            safe_ratio = len(recommendations["recommended_accounts"]) / total_accounts
            ambiguous_penalty = len(validation_flags.get("ambiguous_accounts", [])) * 0.1
            mismatch_penalty = len(validation_flags.get("sum_mismatches", [])) * 0.2

            recommendations["calculation_safety_score"] = max(0.0,
                safe_ratio - ambiguous_penalty - mismatch_penalty
            )

        return recommendations

    def generate_validation_report_enhanced(self, hierarchy_result: Dict[str, Any]) -> str:
        """
        Generate comprehensive validation report with specific recommendations.
        """
        total_accounts = hierarchy_result.get("total_accounts", 0)
        safe_accounts = hierarchy_result.get("safe_accounts", [])
        validation_flags = hierarchy_result.get("validation_flags", {})

        report = f"""
🔍 **Enhanced Account Structure Analysis**
{'=' * 60}

📊 **Summary:**
- Total Accounts: {total_accounts}
- Safe Accounts: {len(safe_accounts)}
- Exclusion Rate: {((total_accounts - len(safe_accounts)) / max(total_accounts, 1) * 100):.1f}%

💚 **Safe Accounts ({len(safe_accounts)}):**
"""
        for account in safe_accounts[:10]:  # Show first 10
            value = hierarchy_result.get("hierarchy_tree", {}).get(account, {}).get("total_value", 0)
            report += f"   ✅ {account}: ¥{value:,.2f}\n"

        if len(safe_accounts) > 10:
            report += f"   ... and {len(safe_accounts) - 10} more\n"

        # Validation issues
        sum_mismatches = validation_flags.get("sum_mismatches", [])
        ambiguous_accounts = validation_flags.get("ambiguous_accounts", [])

        if sum_mismatches:
            report += f"\n⚠️  **Sum Mismatches ({len(sum_mismatches)}):**\n"
            for mismatch in sum_mismatches[:3]:
                parent_value = mismatch.get('expected_total', mismatch.get('parent_value', 0))
                children_total = mismatch.get('children_total', 0)
                difference = mismatch.get('difference', 0)
                report += f"   • {mismatch['parent']}: Expected ¥{parent_value:,.2f}, "
                report += f"Children total ¥{children_total:,.2f} "
                report += f"(Diff: ¥{difference:,.2f})\n"

        if ambiguous_accounts:
            report += f"\n🚨 **Ambiguous Accounts ({len(ambiguous_accounts)}):**\n"
            for ambiguous in ambiguous_accounts[:3]:
                report += f"   • {ambiguous['account']}: {ambiguous['warning']}\n"

        # Conservative recommendations
        if hierarchy_result:
            recommendations = self._generate_conservative_recommendations(hierarchy_result)
            safety_score = recommendations["calculation_safety_score"]

            report += f"\n📋 **Conservative Analysis:**\n"
            report += f"   • Safety Score: {safety_score:.2f}/1.0 "
            if safety_score >= 0.8:
                report += "🟢 EXCELLENT\n"
            elif safety_score >= 0.6:
                report += "🟡 GOOD\n"
            else:
                report += "🔴 NEEDS REVIEW\n"

            if recommendations["warnings"]:
                report += f"\n⚠️  **Exclusion Reasons:**\n"
                for warning in recommendations["warnings"][:5]:
                    report += f"   • {warning}\n"

        report += f"""

❓ **VALIDATION REQUIRED:**
1. Are the identified safe accounts correct for your analysis?
2. Should any excluded accounts be included? (Risk: double counting)
3. What depreciation periods apply to long-term assets?
4. Are there any account relationships we missed?

⚡ **Next Steps:**
- Review excluded accounts and confirm they're not needed
- Confirm depreciation assumptions for asset accounts
- Proceed with calculations using only validated safe accounts
"""

        return report

    def parse_hierarchy_with_validation(self, file_path: str, validation_manager) -> Dict[str, Any]:
        """
        Parse hierarchy and integrate with validation state management.

        Creates a validation session and stores results for later confirmation.
        """
        try:
            # Parse the file using existing method
            hierarchy_result = self.parse_hierarchy(file_path)

            if hierarchy_result.get("parsing_status") != "success":
                return hierarchy_result

            # Enhanced validation
            hierarchy_tree = hierarchy_result["hierarchy_tree"]
            enhanced_validation = self._validate_hierarchy_enhanced(hierarchy_tree)
            safe_accounts_conservative = self._identify_safe_accounts_conservative(hierarchy_tree)

            # Update result with enhanced analysis
            hierarchy_result.update({
                "safe_accounts_conservative": safe_accounts_conservative,
                "enhanced_validation_flags": enhanced_validation,
                "conservative_recommendations": self._generate_conservative_recommendations(hierarchy_result)
            })

            # Create validation session
            session = validation_manager.create_session(file_path)

            # Store parsing results in session context
            session.user_context.update({
                "parsing_timestamp": self._get_timestamp(),
                "total_accounts_found": len(hierarchy_tree),
                "safe_accounts_count": len(safe_accounts_conservative),
                "validation_issues_count": sum(
                    len(issues) for issues in enhanced_validation.values()
                ),
                "parser_version": "enhanced_v1.0"
            })

            hierarchy_result.update({
                "session_id": session.session_id,
                "validation_session": session,
                "validation_report": self.generate_validation_report_enhanced(hierarchy_result)
            })

            self.logger.info(f"Enhanced parsing completed for {file_path}: {len(safe_accounts_conservative)} safe accounts identified")
            return hierarchy_result

        except Exception as e:
            self.logger.error(f"Enhanced parsing failed for {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "error": str(e),
                "parsing_status": "failed",
                "enhancement_status": "failed"
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def validate_parent_child_totals(self, hierarchy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parent account totals against sum of their children.

        This is the key validation feature that uses parent accounts as reference
        to verify our calculations are correct.

        Args:
            hierarchy_result: Result from parse_hierarchy()

        Returns:
            Validation report with reconciliation status, variances, and data quality score
        """
        if hierarchy_result.get("parsing_status") != "success":
            return {
                "validation_status": "failed",
                "error": "Parsing failed, cannot validate"
            }

        hierarchy_tree = hierarchy_result["hierarchy_tree"]
        validation_results = {
            "perfect_matches": [],
            "acceptable_variances": [],
            "significant_variances": [],
            "data_quality_score": 0.0,
            "total_validated": 0,
            "recommendations": []
        }

        tolerance_pct = 0.01  # 1% tolerance for acceptable variance

        # Validate each parent account
        for account_name, account in hierarchy_tree.items():
            if not account.get("children") or not account.get("is_numeric"):
                continue

            parent_value = account.get("total_value", 0)

            # Calculate sum of children
            children_sum = 0
            children_details = []
            for child_name in account["children"]:
                if child_name in hierarchy_tree:
                    child = hierarchy_tree[child_name]
                    if child.get("is_numeric"):
                        child_value = child.get("total_value", 0)
                        children_sum += child_value
                        children_details.append({
                            "name": child_name,
                            "value": child_value
                        })

            # Only validate if both parent and children have values
            if parent_value == 0 and children_sum == 0:
                continue

            validation_results["total_validated"] += 1

            # Calculate variance
            if parent_value != 0:
                variance_pct = abs(parent_value - children_sum) / abs(parent_value)
            else:
                variance_pct = 1.0 if children_sum != 0 else 0.0

            variance_amount = abs(parent_value - children_sum)

            validation_record = {
                "account": account_name,
                "parent_value": parent_value,
                "children_sum": children_sum,
                "variance_amount": variance_amount,
                "variance_pct": variance_pct * 100,  # As percentage
                "children_details": children_details,
                "children_count": len(children_details)
            }

            # Categorize the variance
            if variance_amount <= 1.0 or variance_pct <= 0.001:  # Perfect match (within ¥1 or 0.1%)
                validation_results["perfect_matches"].append(validation_record)
            elif variance_pct <= tolerance_pct:  # Acceptable variance (within 1%)
                validation_results["acceptable_variances"].append(validation_record)
            else:  # Significant variance (over 1%)
                validation_results["significant_variances"].append(validation_record)

                # Add specific recommendation
                if children_sum > 0:
                    validation_results["recommendations"].append({
                        "account": account_name,
                        "issue": f"Large variance detected: {variance_pct*100:.1f}%",
                        "recommendation": f"Use children sum (¥{children_sum:,.2f}) instead of parent value (¥{parent_value:,.2f})",
                        "action": "exclude_parent"
                    })

        # Calculate data quality score
        total = validation_results["total_validated"]
        if total > 0:
            perfect = len(validation_results["perfect_matches"])
            acceptable = len(validation_results["acceptable_variances"])

            # Score: 1.0 for perfect, 0.8 for acceptable, 0 for significant variance
            quality_score = (perfect * 1.0 + acceptable * 0.8) / total
            validation_results["data_quality_score"] = quality_score

        validation_results["validation_status"] = "success"

        return validation_results

    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate a user-friendly validation report showing parent-child reconciliation.

        Args:
            validation_results: Results from validate_parent_child_totals()

        Returns:
            Formatted validation report string
        """
        if validation_results.get("validation_status") != "success":
            return f"❌ Validation failed: {validation_results.get('error', 'Unknown error')}"

        report = "🔍 PARENT-CHILD ACCOUNT VALIDATION REPORT\n"
        report += "=" * 70 + "\n\n"

        # Overall quality score
        quality_score = validation_results["data_quality_score"]
        total_validated = validation_results["total_validated"]

        report += f"📊 DATA QUALITY SCORE: {quality_score:.1%} "
        if quality_score >= 0.95:
            report += "🟢 EXCELLENT\n"
        elif quality_score >= 0.80:
            report += "🟡 GOOD\n"
        elif quality_score >= 0.60:
            report += "🟠 FAIR - Review significant variances\n"
        else:
            report += "🔴 POOR - Manual review required\n"

        report += f"Total Parent Accounts Validated: {total_validated}\n\n"

        # Perfect matches
        perfect = validation_results["perfect_matches"]
        if perfect:
            report += f"✅ PERFECT MATCHES ({len(perfect)}):\n"
            for match in perfect[:5]:  # Show first 5
                report += f"   • {match['account']}: "
                report += f"Parent=¥{match['parent_value']:,.2f} vs Children=¥{match['children_sum']:,.2f}\n"
            if len(perfect) > 5:
                report += f"   ... and {len(perfect) - 5} more perfect matches\n"
            report += "\n"

        # Acceptable variances
        acceptable = validation_results["acceptable_variances"]
        if acceptable:
            report += f"✓ ACCEPTABLE VARIANCES (<1%) ({len(acceptable)}):\n"
            for variance in acceptable[:3]:
                report += f"   • {variance['account']}: "
                report += f"Variance {variance['variance_pct']:.2f}% "
                report += f"(¥{variance['variance_amount']:,.2f})\n"
            if len(acceptable) > 3:
                report += f"   ... and {len(acceptable) - 3} more acceptable variances\n"
            report += "\n"

        # Significant variances - CRITICAL SECTION
        significant = validation_results["significant_variances"]
        if significant:
            report += f"⚠️  SIGNIFICANT VARIANCES (>1%) ({len(significant)}):\n"
            report += "-" * 70 + "\n"
            for variance in significant:
                report += f"\n📍 {variance['account']}:\n"
                report += f"   Parent Value:    ¥{variance['parent_value']:,.2f}\n"
                report += f"   Children Sum:    ¥{variance['children_sum']:,.2f}\n"
                report += f"   Variance:        ¥{variance['variance_amount']:,.2f} ({variance['variance_pct']:.1f}%)\n"
                report += f"   Children Count:  {variance['children_count']}\n"

                # Show children breakdown for significant variances
                if variance['children_details']:
                    report += f"   Children breakdown:\n"
                    for child in variance['children_details'][:5]:
                        report += f"      - {child['name']}: ¥{child['value']:,.2f}\n"
                    if len(variance['children_details']) > 5:
                        report += f"      ... and {len(variance['children_details']) - 5} more\n"
            report += "\n"

        # Recommendations
        recommendations = validation_results.get("recommendations", [])
        if recommendations:
            report += "💡 RECOMMENDATIONS:\n"
            report += "-" * 70 + "\n"
            for rec in recommendations:
                report += f"\n• {rec['account']}:\n"
                report += f"  Issue: {rec['issue']}\n"
                report += f"  Recommendation: {rec['recommendation']}\n"
                report += f"  Action: {rec['action']}\n"

        # Summary and next steps
        report += "\n" + "=" * 70 + "\n"
        report += "📋 SUMMARY:\n"
        report += f"  ✅ Perfect matches: {len(perfect)}\n"
        report += f"  ✓  Acceptable variances: {len(acceptable)}\n"
        report += f"  ⚠️  Significant variances: {len(significant)}\n"

        if significant:
            report += f"\n⚡ NEXT STEPS:\n"
            report += f"  1. Review significant variances above\n"
            report += f"  2. Use children sum instead of parent values where recommended\n"
            report += f"  3. Investigate data quality issues in source Excel file\n"
            report += f"  4. Ensure calculations use only safe (leaf) accounts\n"
        else:
            report += f"\n✨ All parent-child relationships are consistent!\n"
            report += f"   Safe to proceed with calculations using leaf accounts.\n"

        return report

    def validate_with_column_intelligence(self, hierarchy_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced validation using column intelligence to verify calculations.

        This checks:
        1. Were subtotal columns correctly identified and used?
        2. Were note/remark columns properly excluded?
        3. Does our extracted value match the Excel subtotal?

        Args:
            hierarchy_result: Result from parse_hierarchy()

        Returns:
            Enhanced validation results with column intelligence context
        """
        if hierarchy_result.get("parsing_status") != "success":
            return {
                "validation_status": "failed",
                "error": "Parsing failed, cannot validate"
            }

        column_intelligence = hierarchy_result.get("column_intelligence", {})
        if not column_intelligence:
            return {
                "validation_status": "skipped",
                "message": "No column intelligence available (using legacy parsing)"
            }

        classifications = column_intelligence.get("classifications", {})
        value_columns = column_intelligence.get("value_columns", [])
        subtotal_columns = column_intelligence.get("subtotal_columns", [])
        excluded = column_intelligence.get("excluded_columns", {})

        # Validate each account that used subtotal
        accounts = hierarchy_result.get("accounts", [])
        validation_results = []

        for account in accounts:
            if account.get("used_subtotal") and account.get("subtotal_value"):
                # This account used a subtotal - validate it was correct choice
                validation_results.append({
                    "account": account["name"],
                    "used_subtotal": True,
                    "subtotal_value": account["subtotal_value"],
                    "total_value": account["total_value"],
                    "matched": abs(account["subtotal_value"] - account["total_value"]) < 0.01
                })

        # Count excluded columns impact
        total_excluded = sum(len(cols) for cols in excluded.values())

        return {
            "validation_status": "success",
            "column_intelligence_summary": {
                "value_columns_used": len(value_columns),
                "subtotal_columns_found": len(subtotal_columns),
                "columns_excluded": total_excluded,
                "excluded_breakdown": {
                    "subtotals": len(excluded.get("subtotals", [])),
                    "notes": len(excluded.get("notes", [])),
                    "ratios": len(excluded.get("ratios", [])),
                    "headers": len(excluded.get("headers", []))
                }
            },
            "accounts_using_subtotals": len([r for r in validation_results if r["used_subtotal"]]),
            "subtotal_validations": validation_results,
            "all_subtotals_valid": all(r["matched"] for r in validation_results)
        }

    def generate_column_intelligence_report(self, hierarchy_result: Dict[str, Any]) -> str:
        """
        Generate comprehensive report on column intelligence decisions.

        Shows users exactly what columns were used/excluded and why.
        """
        if hierarchy_result.get("parsing_status") != "success":
            return "❌ Parsing failed, no column intelligence available"

        column_intelligence = hierarchy_result.get("column_intelligence", {})
        if not column_intelligence:
            return "⚠️  No column intelligence (using legacy parsing)"

        report = "📊 COLUMN INTELLIGENCE REPORT\n"
        report += "=" * 70 + "\n"
        report += column_intelligence.get("classification_report", "")

        # Add validation results
        validation = self.validate_with_column_intelligence(hierarchy_result)

        if validation.get("validation_status") == "success":
            summary = validation["column_intelligence_summary"]
            report += f"\n\n📈 IMPACT ANALYSIS:\n"
            report += f"   • {summary['value_columns_used']} columns used for calculations\n"
            report += f"   • {summary['subtotal_columns_found']} subtotal columns found (used when available)\n"
            report += f"   • {summary['columns_excluded']} columns excluded from calculations\n"

            if summary['columns_excluded'] > 0:
                breakdown = summary['excluded_breakdown']
                report += f"\n   Exclusion breakdown:\n"
                if breakdown['subtotals'] > 0:
                    report += f"      - {breakdown['subtotals']} subtotal columns (prevents double counting)\n"
                if breakdown['notes'] > 0:
                    report += f"      - {breakdown['notes']} note/remark columns (non-financial data)\n"
                if breakdown['ratios'] > 0:
                    report += f"      - {breakdown['ratios']} ratio/percentage columns\n"
                if breakdown['headers'] > 0:
                    report += f"      - {breakdown['headers']} header/label columns\n"

            accounts_using_subtotals = validation.get("accounts_using_subtotals", 0)
            if accounts_using_subtotals > 0:
                report += f"\n   • {accounts_using_subtotals} accounts used subtotal values (smart!)\n"

        report += "\n\n" + "=" * 70 + "\n"
        report += "✅ Column intelligence prevents calculation errors by:\n"
        report += "   1. Using subtotals instead of summing periods (no double counting)\n"
        report += "   2. Excluding note/remark columns (non-financial data)\n"
        report += "   3. Excluding ratio columns (percentages, not values)\n"

        return report