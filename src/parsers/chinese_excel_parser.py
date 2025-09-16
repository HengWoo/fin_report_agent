"""
Chinese Excel Parser for Restaurant Financial Statements

This module handles parsing of Chinese restaurant financial Excel files,
specifically income statements with multi-period data.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ChineseExcelParser:
    """Parser for Chinese restaurant financial Excel files."""

    def __init__(self):
        self.chinese_terms = {
            "项目": "line_item",
            "营业收入": "operating_revenue",
            "食品收入": "food_revenue",
            "酒水收入": "beverage_revenue",
            "甜品/糖水收入": "dessert_revenue",
            "其他收入": "other_revenue",
            "折扣": "discount",
            "主营业务成本": "cogs",
            "食品成本": "food_cost",
            "酒水成本": "beverage_cost",
            "甜品/糖水成本": "dessert_cost",
            "毛利": "gross_profit",
            "毛利率": "gross_margin",
            "营业费用": "operating_expenses",
            "人工成本": "labor_cost",
            "工资": "wages",
            "社保/商业保险": "insurance",
            "租赁费用": "rent_expense",
            "门面房租": "storefront_rent",
            "宿舍租金": "dormitory_rent",
            "物业费": "property_management",
            "占比": "percentage"
        }

    def parse_income_statement(self, file_path: str) -> Dict[str, Any]:
        """
        Parse Chinese restaurant income statement from Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            Dictionary containing parsed financial data
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            logger.info(f"Loaded Excel file: {file_path}")

            # Extract basic structure info
            structure = self._analyze_structure(df)

            # Extract time periods
            periods = self._extract_periods(df)

            # Parse financial data
            financial_data = self._parse_financial_data(df, periods)

            return {
                "file_path": file_path,
                "structure": structure,
                "periods": periods,
                "financial_data": financial_data,
                "parsing_status": "success"
            }

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "error": str(e),
                "parsing_status": "failed"
            }

    def _analyze_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the structure of the Excel sheet."""
        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "non_empty_rows": len(df.dropna(how="all")),
            "detected_header_row": self._detect_header_row(df)
        }

    def _detect_header_row(self, df: pd.DataFrame) -> int:
        """Detect which row contains the headers."""
        # Look for row containing "项目" and period indicators
        for i in range(min(10, len(df))):
            row_values = df.iloc[i].astype(str).values
            if any("项目" in str(val) for val in row_values):
                return i
        return 0

    def _extract_periods(self, df: pd.DataFrame) -> List[str]:
        """Extract time periods from the Excel headers."""
        periods = []

        # Get the first few rows to find period headers
        header_rows = df.head(3)

        for col in df.columns:
            col_str = str(col)
            # Look for month patterns
            if any(month in col_str for month in ["月", "年"]):
                periods.append(col_str)
            # Look for period patterns in cell values
            for _, row in header_rows.iterrows():
                cell_value = str(row[col])
                if any(pattern in cell_value for pattern in ["月", "年", "占比"]):
                    if cell_value not in periods:
                        periods.append(cell_value)

        # Clean and deduplicate
        periods = [p for p in periods if p != "nan" and len(p.strip()) > 0]
        return list(dict.fromkeys(periods))  # Remove duplicates while preserving order

    def _parse_financial_data(self, df: pd.DataFrame, periods: List[str]) -> Dict[str, Any]:
        """Parse the actual financial data from the sheet."""
        financial_data = {}

        # Handle empty DataFrame
        if df.empty or len(df.columns) == 0:
            return financial_data

        # Find the column containing line items (项目)
        line_item_col = None
        for col in df.columns:
            if df[col].astype(str).str.contains("项目", na=False).any():
                line_item_col = col
                break

        if line_item_col is None:
            line_item_col = df.columns[0]  # Default to first column

        # Extract line items and their values
        for idx, row in df.iterrows():
            line_item = str(row[line_item_col]).strip()

            # Skip empty or header rows
            if pd.isna(row[line_item_col]) or line_item == "nan" or "项目" in line_item:
                continue

            # Translate Chinese term if available
            english_term = self.chinese_terms.get(line_item, line_item)

            # Extract values for each period
            row_data = {}
            for col in df.columns:
                if col != line_item_col:
                    value = row[col]
                    if pd.notna(value) and isinstance(value, (int, float)):
                        row_data[str(col)] = float(value)

            if row_data:  # Only add if we have data
                financial_data[english_term] = {
                    "chinese_term": line_item,
                    "values": row_data
                }

        return financial_data

    def get_supported_terms(self) -> Dict[str, str]:
        """Get dictionary of supported Chinese terms and their English equivalents."""
        return self.chinese_terms.copy()


def create_sample_data() -> pd.DataFrame:
    """Create sample data for testing when real files are not available."""
    data = {
        "项目": [
            "项目", "一、营业收入", "食品收入", "酒水收入", "甜品收入",
            "折扣", "减:主营业务成本", "食品成本", "酒水成本",
            "二、毛利", "毛利率", "营业费用", "人工成本"
        ],
        "1月": [
            "1月", 500000, 400000, 50000, 40000,
            -10000, 200000, 160000, 20000,
            290000, 0.58, 150000, 80000
        ],
        "占比": [
            "占比", None, 0.8, 0.1, 0.08,
            -0.02, 0.4, 0.32, 0.04,
            0.58, None, 0.3, 0.16
        ],
        "2月": [
            "2月", 520000, 410000, 55000, 45000,
            -10000, 210000, 165000, 25000,
            300000, 0.577, 155000, 85000
        ]
    }

    return pd.DataFrame(data)


if __name__ == "__main__":
    # Demo usage
    parser = ChineseExcelParser()

    # Create sample data for testing
    sample_df = create_sample_data()
    print("Sample data created:")
    print(sample_df)

    print("\nSupported Chinese terms:")
    for chinese, english in parser.get_supported_terms().items():
        print(f"  {chinese} -> {english}")