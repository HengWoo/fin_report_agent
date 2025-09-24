"""
Column Intelligence System for Excel Financial Reports

This module provides intelligent column classification to prevent common parsing errors:
- Double counting from subtotal columns
- Including note/remark columns in calculations
- Misidentifying ratio/percentage columns as values

Key insight: Understanding column PURPOSE is critical for accurate financial analysis.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)


class ColumnType(Enum):
    """Types of columns in financial Excel files."""
    PERIOD = "period"           # Time period data (May, June, Q1, etc.)
    VALUE = "value"             # Numeric value column (no clear period marker)
    SUBTOTAL = "subtotal"       # Total/subtotal column (合计, 总计, 小计)
    NOTE = "note"               # Notes/remarks column (备注, 说明)
    RATIO = "ratio"             # Ratio/percentage column (占比, %)
    HEADER = "header"           # Header/label column
    UNKNOWN = "unknown"         # Unclassified


class ColumnClassifier:
    """
    Intelligent column classifier for financial Excel files.

    Prevents calculation errors by understanding column purpose.
    """

    def __init__(self):
        """Initialize column classifier with pattern definitions."""

        # Chinese and English patterns for different column types
        self.SUBTOTAL_PATTERNS = [
            '合计', '总计', '小计', '汇总',  # Chinese
            'Total', 'Subtotal', 'Sum', 'Grand Total',  # English
            '总额', '累计'
        ]

        self.NOTE_PATTERNS = [
            '备注', '说明', '附注', '注释',  # Chinese
            'Notes', 'Remark', 'Comment', 'Memo',  # English
            '说明栏', '附件'
        ]

        self.RATIO_PATTERNS = [
            '占比', '比例', '百分比', '率',  # Chinese
            'Ratio', 'Percentage', 'Rate', '%',  # English
            '同比', '环比', '增长率'
        ]

        self.PERIOD_PATTERNS = [
            # Chinese month/quarter patterns
            '月', '季度', '年', '上半年', '下半年',
            # English patterns
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
            'Q1', 'Q2', 'Q3', 'Q4', 'Quarter',
            # Number patterns for months
            '1月', '2月', '3月', '4月', '5月', '6月',
            '7月', '8月', '9月', '10月', '11月', '12月'
        ]

        # Cache for performance
        self._classification_cache: Dict[str, ColumnType] = {}

    def classify_columns(self, df: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
        """
        Classify all columns in a DataFrame.

        Handles two cases:
        1. Headers in column names (standard Excel)
        2. Headers in first data row (Chinese financial reports)

        Args:
            df: DataFrame to classify

        Returns:
            Dictionary mapping column index to classification info
        """
        classifications = {}

        # Check if we need to use first row as headers
        # (when column names are generic like "Unnamed: X")
        use_first_row_as_headers = self._should_use_first_row_as_headers(df)

        if use_first_row_as_headers:
            logger.info("Using first data row as column headers (Chinese format detected)")

        for col_idx in range(len(df.columns)):
            # Get header from column name or first row
            if use_first_row_as_headers and len(df) > 0:
                header = str(df.iloc[0, col_idx]) if pd.notna(df.iloc[0, col_idx]) else f"Column_{col_idx}"
            else:
                header = str(df.columns[col_idx]) if col_idx < len(df.columns) else f"Column_{col_idx}"

            # Classify the column
            col_type = self._classify_single_column(header, df.iloc[:, col_idx])

            # Sample values for validation (skip first row if it's headers)
            sample_values = []
            start_row = 1 if use_first_row_as_headers else 0
            for value in df.iloc[start_row:start_row+10, col_idx]:
                if pd.notna(value):
                    sample_values.append(value)

            classifications[col_idx] = {
                "index": col_idx,
                "header": header,
                "type": col_type,
                "sample_values": sample_values[:3],  # First 3 non-null values
                "include_in_calculations": self._should_include_in_calculations(col_type),
                "header_from_first_row": use_first_row_as_headers
            }

        logger.info(f"Classified {len(classifications)} columns")
        return classifications

    def _should_use_first_row_as_headers(self, df: pd.DataFrame) -> bool:
        """
        Determine if first data row should be used as column headers.

        This is common in Chinese financial Excel files where:
        - Column names are generic (Unnamed: X)
        - First row contains actual headers (损益类别, 合计, 备注, etc.)

        Args:
            df: DataFrame to check

        Returns:
            True if first row should be used as headers
        """
        if len(df) == 0:
            return False

        # Check if column names are mostly generic
        generic_count = sum(1 for col in df.columns if str(col).startswith('Unnamed:'))
        total_cols = len(df.columns)

        # If >50% columns are "Unnamed:", likely need first row as headers
        if generic_count / total_cols > 0.5:
            # Verify first row looks like headers (mostly strings)
            first_row = df.iloc[0]
            string_count = sum(1 for val in first_row if isinstance(val, str))

            # If >50% of first row values are strings, it's likely headers
            return string_count / len(first_row) > 0.5

        return False

    def _classify_single_column(self, header: str, data: pd.Series) -> ColumnType:
        """
        Classify a single column based on header and data.

        Args:
            header: Column header text
            data: Column data series

        Returns:
            ColumnType classification
        """
        # Check cache
        if header in self._classification_cache:
            return self._classification_cache[header]

        header_lower = header.lower().strip()

        # Priority order matters!

        # 1. Check for subtotal patterns (HIGHEST PRIORITY - must exclude these!)
        if any(pattern in header for pattern in self.SUBTOTAL_PATTERNS):
            col_type = ColumnType.SUBTOTAL

        # 2. Check for note patterns
        elif any(pattern in header for pattern in self.NOTE_PATTERNS):
            col_type = ColumnType.NOTE

        # 3. Check for ratio patterns
        elif any(pattern in header for pattern in self.RATIO_PATTERNS):
            col_type = ColumnType.RATIO

        # 4. Check for period patterns
        elif any(pattern in header for pattern in self.PERIOD_PATTERNS):
            col_type = ColumnType.PERIOD

        # 5. Check if it's a header/label column (mostly text)
        elif self._is_header_column(data):
            col_type = ColumnType.HEADER

        # 6. Check if it has numeric values (likely a value column)
        elif self._has_numeric_values(data):
            col_type = ColumnType.VALUE

        else:
            col_type = ColumnType.UNKNOWN

        # Cache the result
        self._classification_cache[header] = col_type

        return col_type

    def _is_header_column(self, data: pd.Series) -> bool:
        """Check if column is primarily text/labels."""
        non_null = data.dropna()
        if len(non_null) == 0:
            return False

        # If more than 80% are strings, it's likely a header column
        string_count = sum(1 for val in non_null if isinstance(val, str))
        return string_count / len(non_null) > 0.8

    def _has_numeric_values(self, data: pd.Series) -> bool:
        """Check if column has significant numeric content."""
        non_null = data.dropna()
        if len(non_null) == 0:
            return False

        # If more than 50% are numeric, consider it a value column
        numeric_count = sum(1 for val in non_null if isinstance(val, (int, float)))
        return numeric_count / len(non_null) > 0.5

    def _should_include_in_calculations(self, col_type: ColumnType) -> bool:
        """
        Determine if a column should be included in value calculations.

        Critical logic:
        - SUBTOTAL: NO (would cause double counting)
        - NOTE: NO (not financial data)
        - RATIO: NO (percentages, not absolute values)
        - PERIOD: YES (actual financial data)
        - VALUE: YES (actual financial data)
        - HEADER: NO (labels only)
        """
        include_types = {ColumnType.PERIOD, ColumnType.VALUE}
        return col_type in include_types

    def get_value_columns(self, classifications: Dict[int, Dict[str, Any]]) -> List[int]:
        """Get list of column indices that should be included in calculations."""
        return [
            col_idx for col_idx, info in classifications.items()
            if info["include_in_calculations"]
        ]

    def get_subtotal_columns(self, classifications: Dict[int, Dict[str, Any]]) -> List[int]:
        """Get list of subtotal column indices (for validation)."""
        return [
            col_idx for col_idx, info in classifications.items()
            if info["type"] == ColumnType.SUBTOTAL
        ]

    def get_excluded_columns(self, classifications: Dict[int, Dict[str, Any]]) -> Dict[str, List[int]]:
        """Get columns excluded from calculations, grouped by reason."""
        excluded = {
            "subtotals": [],
            "notes": [],
            "ratios": [],
            "headers": [],
            "unknown": []
        }

        for col_idx, info in classifications.items():
            if not info["include_in_calculations"]:
                col_type = info["type"]
                if col_type == ColumnType.SUBTOTAL:
                    excluded["subtotals"].append(col_idx)
                elif col_type == ColumnType.NOTE:
                    excluded["notes"].append(col_idx)
                elif col_type == ColumnType.RATIO:
                    excluded["ratios"].append(col_idx)
                elif col_type == ColumnType.HEADER:
                    excluded["headers"].append(col_idx)
                else:
                    excluded["unknown"].append(col_idx)

        return excluded

    def generate_classification_report(self,
                                      df: pd.DataFrame,
                                      classifications: Dict[int, Dict[str, Any]]) -> str:
        """Generate human-readable classification report."""

        value_cols = self.get_value_columns(classifications)
        subtotal_cols = self.get_subtotal_columns(classifications)
        excluded = self.get_excluded_columns(classifications)

        report = "📊 COLUMN INTELLIGENCE REPORT\n"
        report += "=" * 70 + "\n\n"

        # Value columns (included in calculations)
        report += f"✅ VALUE COLUMNS (included in calculations): {len(value_cols)}\n"
        for col_idx in value_cols[:10]:  # Show first 10
            info = classifications[col_idx]
            report += f"   • Column {col_idx}: {info['header']} [{info['type'].value}]\n"
        if len(value_cols) > 10:
            report += f"   ... and {len(value_cols) - 10} more\n"

        # Subtotal columns (for validation only)
        if subtotal_cols:
            report += f"\n🔍 SUBTOTAL COLUMNS (validation only): {len(subtotal_cols)}\n"
            for col_idx in subtotal_cols:
                info = classifications[col_idx]
                report += f"   • Column {col_idx}: {info['header']}\n"
                report += f"     ⚠️  NOT included in sum (prevents double counting)\n"

        # Excluded columns
        total_excluded = sum(len(cols) for cols in excluded.values())
        if total_excluded > 0:
            report += f"\n🚫 EXCLUDED COLUMNS: {total_excluded}\n"

            if excluded["notes"]:
                report += f"   📝 Notes/Remarks ({len(excluded['notes'])}):\n"
                for col_idx in excluded["notes"][:3]:
                    info = classifications[col_idx]
                    report += f"      • Column {col_idx}: {info['header']}\n"

            if excluded["ratios"]:
                report += f"   📊 Ratios/Percentages ({len(excluded['ratios'])}):\n"
                for col_idx in excluded["ratios"][:3]:
                    info = classifications[col_idx]
                    report += f"      • Column {col_idx}: {info['header']}\n"

            if excluded["headers"]:
                report += f"   🏷️  Header/Label ({len(excluded['headers'])}):\n"

        report += "\n" + "=" * 70 + "\n"
        report += "❓ VALIDATION QUESTION:\n"
        report += "Is this column classification correct for your analysis?\n"

        return report

    def validate_with_subtotals(self,
                                row_data: pd.Series,
                                classifications: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate calculated sum against subtotal columns.

        Args:
            row_data: Row of data to validate
            classifications: Column classifications

        Returns:
            Validation results with variance info
        """
        value_cols = self.get_value_columns(classifications)
        subtotal_cols = self.get_subtotal_columns(classifications)

        # Calculate sum from value columns only
        calculated_sum = 0
        for col_idx in value_cols:
            value = row_data.iloc[col_idx]
            if pd.notna(value) and isinstance(value, (int, float)):
                calculated_sum += value

        # Check against subtotal columns
        validation_results = []
        for col_idx in subtotal_cols:
            subtotal_value = row_data.iloc[col_idx]
            if pd.notna(subtotal_value) and isinstance(subtotal_value, (int, float)) and subtotal_value != 0:
                variance = abs(calculated_sum - subtotal_value)
                variance_pct = variance / abs(subtotal_value) if subtotal_value != 0 else 0

                validation_results.append({
                    "subtotal_column": col_idx,
                    "subtotal_header": classifications[col_idx]["header"],
                    "expected": subtotal_value,
                    "calculated": calculated_sum,
                    "variance": variance,
                    "variance_pct": variance_pct * 100,
                    "valid": variance <= max(abs(subtotal_value) * 0.01, 1.0)  # 1% tolerance
                })

        return {
            "calculated_sum": calculated_sum,
            "validations": validation_results,
            "all_valid": all(v["valid"] for v in validation_results)
        }