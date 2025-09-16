"""
Unit tests for the Chinese Excel Parser.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parsers.chinese_excel_parser import ChineseExcelParser, create_sample_data


class TestChineseExcelParser:
    """Test cases for ChineseExcelParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ChineseExcelParser()

    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        assert self.parser is not None
        assert isinstance(self.parser.chinese_terms, dict)
        assert len(self.parser.chinese_terms) > 0

    def test_chinese_terms_mapping(self):
        """Test Chinese terms are mapped correctly."""
        terms = self.parser.get_supported_terms()

        # Check key mappings
        assert terms["营业收入"] == "operating_revenue"
        assert terms["食品收入"] == "food_revenue"
        assert terms["酒水收入"] == "beverage_revenue"
        assert terms["毛利率"] == "gross_margin"
        assert terms["人工成本"] == "labor_cost"

    def test_detect_header_row(self):
        """Test header row detection."""
        # Create sample dataframe with header in row 1
        data = {
            "col1": ["", "项目", "一、营业收入"],
            "col2": ["", "1月", "500000"],
            "col3": ["", "2月", "520000"]
        }
        df = pd.DataFrame(data)

        header_row = self.parser._detect_header_row(df)
        assert header_row == 1

    def test_extract_periods(self):
        """Test period extraction from headers."""
        # Create sample dataframe with periods
        data = {
            "项目": ["项目", "营业收入"],
            "1月": ["1月", 500000],
            "占比": ["占比", 0.8],
            "2月": ["2月", 520000],
            "2025年总计": ["2025年总计", 1020000]
        }
        df = pd.DataFrame(data)

        periods = self.parser._extract_periods(df)

        # Should extract month and year patterns
        month_periods = [p for p in periods if "月" in p]
        year_periods = [p for p in periods if "年" in p]

        assert len(month_periods) >= 2  # At least 1月, 2月
        assert len(year_periods) >= 1   # At least 2025年总计

    def test_parse_financial_data(self):
        """Test financial data parsing."""
        # Create sample dataframe
        data = {
            "项目": ["项目", "营业收入", "食品收入", "毛利"],
            "1月": ["1月", 500000, 400000, 300000],
            "2月": ["2月", 520000, 410000, 310000]
        }
        df = pd.DataFrame(data)
        periods = ["1月", "2月"]

        financial_data = self.parser._parse_financial_data(df, periods)

        # Check that data was extracted
        assert len(financial_data) >= 2

        # Check specific mappings
        if "operating_revenue" in financial_data:
            revenue_data = financial_data["operating_revenue"]
            assert revenue_data["chinese_term"] == "营业收入"
            assert "1月" in revenue_data["values"]
            assert revenue_data["values"]["1月"] == 500000.0

    def test_create_sample_data(self):
        """Test sample data creation."""
        df = create_sample_data()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "项目" in df.columns
        assert "1月" in df.columns

        # Check that we have revenue data
        revenue_row = df[df["项目"] == "一、营业收入"]
        assert len(revenue_row) > 0
        assert revenue_row["1月"].iloc[0] > 0

    def test_parse_income_statement_success(self):
        """Test successful parsing of income statement."""
        # This test requires the sample Excel file to exist
        file_path = "data/sample_restaurant_income_2025.xlsx"

        if Path(file_path).exists():
            result = self.parser.parse_income_statement(file_path)

            assert result["parsing_status"] == "success"
            assert "structure" in result
            assert "periods" in result
            assert "financial_data" in result

            # Check structure
            structure = result["structure"]
            assert "shape" in structure
            assert "columns" in structure

            # Check that we extracted some financial data
            financial_data = result["financial_data"]
            assert len(financial_data) > 0
        else:
            pytest.skip("Sample Excel file not found")

    def test_parse_income_statement_file_not_found(self):
        """Test parsing with non-existent file."""
        result = self.parser.parse_income_statement("nonexistent_file.xlsx")

        assert result["parsing_status"] == "failed"
        assert "error" in result

    def test_analyze_structure(self):
        """Test structure analysis."""
        # Create sample dataframe
        data = {
            "col1": ["", "项目", "营业收入", "", "食品收入"],
            "col2": ["", "1月", 500000, None, 400000],
            "col3": ["", "2月", 520000, None, 410000]
        }
        df = pd.DataFrame(data)

        structure = self.parser._analyze_structure(df)

        assert "shape" in structure
        assert "columns" in structure
        assert "non_empty_rows" in structure
        assert "detected_header_row" in structure

        assert structure["shape"] == (5, 3)
        assert len(structure["columns"]) == 3

    def test_error_handling(self):
        """Test error handling with malformed data."""
        # Create dataframe with no valid financial data
        data = {"random_col": ["random_data"]}
        df = pd.DataFrame(data)

        financial_data = self.parser._parse_financial_data(df, [])

        # Should return empty dict or handle gracefully
        assert isinstance(financial_data, dict)

    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        df = pd.DataFrame()

        periods = self.parser._extract_periods(df)
        assert isinstance(periods, list)

        financial_data = self.parser._parse_financial_data(df, periods)
        assert isinstance(financial_data, dict)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])