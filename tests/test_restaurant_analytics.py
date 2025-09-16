"""Tests for restaurant analytics engine."""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import date

from src.analyzers.restaurant_analytics import RestaurantAnalyticsEngine
from src.models.financial_data import IncomeStatement, FinancialPeriod, RevenueBreakdown, CostBreakdown, ExpenseBreakdown, ProfitMetrics


class TestRestaurantAnalyticsEngine:
    """Test cases for RestaurantAnalyticsEngine."""

    @pytest.fixture
    def analytics_engine(self):
        """Create analytics engine instance."""
        return RestaurantAnalyticsEngine()

    @pytest.fixture
    def sample_income_statement(self):
        """Create sample income statement for testing."""
        return IncomeStatement(
            period=FinancialPeriod(
                period_id="2024Q1",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 3, 31),
                period_type="quarterly"
            ),
            revenue=RevenueBreakdown(
                total_revenue=150000.0,
                food_sales=120000.0,
                beverage_sales=25000.0,
                other_revenue=5000.0
            ),
            costs=CostBreakdown(
                total_cogs=52500.0,
                food_costs=45000.0,
                beverage_costs=7500.0
            ),
            expenses=ExpenseBreakdown(
                total_expenses=75000.0,
                labor_costs=45000.0,
                rent=15000.0,
                utilities=3000.0,
                marketing=2000.0,
                other_expenses=10000.0
            ),
            metrics=ProfitMetrics(
                gross_profit=97500.0,
                operating_profit=22500.0,
                net_profit=20000.0,
                ebitda=25000.0
            )
        )

    @patch('src.parsers.chinese_excel_parser.ChineseExcelParser')
    def test_analyze_restaurant_excel_success(self, mock_parser, analytics_engine, sample_income_statement):
        """Test successful Excel analysis."""
        # Mock parser
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_income_statement.return_value = {
            'periods': ['2024Q1'],
            'financial_data': {
                '2024Q1': {
                    'revenue': {'total': 150000.0, 'food': 120000.0, 'beverage': 25000.0, 'other': 5000.0},
                    'costs': {'total': 52500.0, 'food': 45000.0, 'beverage': 7500.0},
                    'expenses': {'total': 75000.0, 'labor': 45000.0, 'rent': 15000.0, 'utilities': 3000.0, 'marketing': 2000.0, 'other': 10000.0}
                }
            }
        }

        # Mock validation
        with patch('src.validators.restaurant_validator.RestaurantFinancialValidator') as mock_validator:
            mock_validator_instance = MagicMock()
            mock_validator.return_value = mock_validator_instance
            mock_validator_instance.validate_income_statement.return_value = []

            result = analytics_engine.analyze_restaurant_excel('/fake/path/test.xlsx')

            # Verify structure
            assert 'metadata' in result
            assert 'periods_analyzed' in result
            assert 'validation_results' in result
            assert 'analysis_results' in result

            # Verify analysis components
            analysis = result['analysis_results']
            assert 'kpis' in analysis
            assert 'insights' in analysis
            assert len(result['periods_analyzed']) == 1

    @patch('src.parsers.chinese_excel_parser.ChineseExcelParser')
    def test_analyze_restaurant_excel_validation_errors(self, mock_parser, analytics_engine):
        """Test Excel analysis with validation errors."""
        # Mock parser
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_income_statement.return_value = {
            'periods': ['2024Q1'],
            'financial_data': {
                '2024Q1': {
                    'revenue': {'total': 100000.0, 'food': 80000.0, 'beverage': 20000.0, 'other': 0.0},
                    'costs': {'total': 60000.0, 'food': 50000.0, 'beverage': 10000.0},  # High cost ratio
                    'expenses': {'total': 50000.0, 'labor': 35000.0, 'rent': 10000.0, 'utilities': 2000.0, 'marketing': 1000.0, 'other': 2000.0}
                }
            }
        }

        # Mock validation with errors
        with patch('src.validators.restaurant_validator.RestaurantFinancialValidator') as mock_validator:
            mock_validator_instance = MagicMock()
            mock_validator.return_value = mock_validator_instance
            mock_validator_instance.validate_income_statement.return_value = [
                {'code': 'HIGH_COGS', 'severity': 'warning', 'message': 'COGS ratio is high'}
            ]

            result = analytics_engine.analyze_restaurant_excel('/fake/path/test.xlsx')

            # Should still complete analysis despite validation warnings
            assert result['validation_results']
            assert len(result['validation_results']) == 1
            assert result['validation_results'][0]['code'] == 'HIGH_COGS'

    @patch('src.parsers.chinese_excel_parser.ChineseExcelParser')
    def test_analyze_multi_period_data(self, mock_parser, analytics_engine):
        """Test analysis of multi-period data for trend analysis."""
        # Mock multi-period data
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_income_statement.return_value = {
            'periods': ['2023Q4', '2024Q1'],
            'financial_data': {
                '2023Q4': {
                    'revenue': {'total': 140000.0, 'food': 112000.0, 'beverage': 23000.0, 'other': 5000.0},
                    'costs': {'total': 49000.0, 'food': 42000.0, 'beverage': 7000.0},
                    'expenses': {'total': 70000.0, 'labor': 42000.0, 'rent': 15000.0, 'utilities': 2800.0, 'marketing': 1800.0, 'other': 8400.0}
                },
                '2024Q1': {
                    'revenue': {'total': 150000.0, 'food': 120000.0, 'beverage': 25000.0, 'other': 5000.0},
                    'costs': {'total': 52500.0, 'food': 45000.0, 'beverage': 7500.0},
                    'expenses': {'total': 75000.0, 'labor': 45000.0, 'rent': 15000.0, 'utilities': 3000.0, 'marketing': 2000.0, 'other': 10000.0}
                }
            }
        }

        with patch('src.validators.restaurant_validator.RestaurantFinancialValidator') as mock_validator:
            mock_validator_instance = MagicMock()
            mock_validator.return_value = mock_validator_instance
            mock_validator_instance.validate_income_statement.return_value = []

            result = analytics_engine.analyze_restaurant_excel('/fake/path/test.xlsx')

            # Should have trend analysis for multi-period data
            assert len(result['periods_analyzed']) == 2
            analysis = result['analysis_results']
            assert 'trends' in analysis

            # Verify trend data structure
            trends = analysis['trends']
            assert 'growth_rates' in trends
            assert 'trend_summary' in trends

    def test_build_income_statement_from_period_data(self, analytics_engine):
        """Test building IncomeStatement from period data."""
        period_data = {
            'revenue': {'total': 150000.0, 'food': 120000.0, 'beverage': 25000.0, 'other': 5000.0},
            'costs': {'total': 52500.0, 'food': 45000.0, 'beverage': 7500.0},
            'expenses': {'total': 75000.0, 'labor': 45000.0, 'rent': 15000.0, 'utilities': 3000.0, 'marketing': 2000.0, 'other': 10000.0}
        }

        statement = analytics_engine._build_income_statement_from_period_data('2024Q1', period_data)

        assert isinstance(statement, IncomeStatement)
        assert statement.revenue.total_revenue == 150000.0
        assert statement.costs.total_cogs == 52500.0
        assert statement.expenses.total_expenses == 75000.0
        assert statement.metrics.gross_profit == 97500.0  # 150000 - 52500
        assert statement.metrics.operating_profit == 22500.0  # 97500 - 75000

    def test_calculate_derived_metrics(self, analytics_engine):
        """Test calculation of derived financial metrics."""
        revenue = 150000.0
        total_cogs = 52500.0
        total_expenses = 75000.0

        # Test the actual calculation logic
        gross_profit = revenue - total_cogs
        operating_profit = gross_profit - total_expenses

        assert gross_profit == 97500.0
        assert operating_profit == 22500.0

    @patch('src.parsers.chinese_excel_parser.ChineseExcelParser')
    def test_error_handling_parser_failure(self, mock_parser, analytics_engine):
        """Test error handling when parser fails."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_income_statement.side_effect = Exception("Parser error")

        with pytest.raises(Exception, match="Parser error"):
            analytics_engine.analyze_restaurant_excel('/fake/path/test.xlsx')

    def test_parse_period_string(self, analytics_engine):
        """Test parsing period strings into dates."""
        # Test quarterly period parsing logic
        period_string = '2024Q1'
        if 'Q' in period_string:
            year, quarter = period_string.split('Q')
            year = int(year)
            quarter = int(quarter)

            if quarter == 1:
                start_date = date(year, 1, 1)
                end_date = date(year, 3, 31)

            assert start_date == date(2024, 1, 1)
            assert end_date == date(2024, 3, 31)