"""
Comprehensive tests for the validation system.

Tests data models, validation rules, and the complete transformation pipeline.
"""

import pytest
import sys
import os
from decimal import Decimal
from unittest.mock import Mock, patch

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.financial_data import (
    FinancialPeriod,
    RevenueBreakdown,
    CostBreakdown,
    ExpenseBreakdown,
    ProfitMetrics,
    IncomeStatement,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    DataQualityScore,
    PeriodType
)
from src.validators.restaurant_validator import (
    RestaurantFinancialValidator,
    ValidationEngine,
    RestaurantMarginRule,
    FoodCostRatioRule,
    LaborCostRatioRule
)
from src.transformers.data_transformer import DataTransformer, TransformationResult


class TestFinancialDataModels:
    """Test Pydantic financial data models."""

    def test_revenue_breakdown_validation(self):
        """Test revenue breakdown validation."""
        # Valid revenue breakdown
        revenue = RevenueBreakdown(
            total_revenue=Decimal('100000'),
            food_revenue=Decimal('80000'),
            beverage_revenue=Decimal('15000'),
            dessert_revenue=Decimal('5000'),
            discounts=Decimal('0')
        )

        assert revenue.total_revenue == Decimal('100000')
        assert revenue.food_revenue == Decimal('80000')

    def test_revenue_breakdown_negative_validation(self):
        """Test revenue breakdown handles negative values correctly."""
        revenue = RevenueBreakdown(
            total_revenue=Decimal('95000'),
            food_revenue=Decimal('80000'),
            beverage_revenue=Decimal('15000'),
            dessert_revenue=Decimal('5000'),
            discounts=Decimal('-5000')  # Negative discount is normal
        )

        assert revenue.discounts == Decimal('-5000')

    def test_profit_metrics_validation(self):
        """Test profit metrics validation and warnings."""
        # Test with normal restaurant margins
        metrics = ProfitMetrics(
            gross_profit=Decimal('60000'),
            gross_margin=Decimal('0.6'),  # 60% - normal for restaurants
            operating_profit=Decimal('10000'),
            operating_margin=Decimal('0.1'),
            food_cost_ratio=Decimal('0.3'),  # 30% - normal
            labor_cost_ratio=Decimal('0.25'),  # 25% - normal
            prime_cost_ratio=Decimal('0.55')  # 55% - normal
        )

        assert metrics.gross_margin == Decimal('0.6')
        assert metrics.food_cost_ratio == Decimal('0.3')

    def test_income_statement_consistency(self):
        """Test income statement financial consistency validation."""
        period = FinancialPeriod(
            period_id="2025-01",
            period_type=PeriodType.MONTHLY
        )

        revenue = RevenueBreakdown(
            total_revenue=Decimal('100000'),
            food_revenue=Decimal('80000'),
            beverage_revenue=Decimal('20000')
        )

        costs = CostBreakdown(
            total_cogs=Decimal('40000'),
            food_cost=Decimal('32000'),
            beverage_cost=Decimal('8000')
        )

        expenses = ExpenseBreakdown(
            total_operating_expenses=Decimal('35000'),
            labor_cost=Decimal('25000'),
            rent_expense=Decimal('10000')
        )

        metrics = ProfitMetrics(
            gross_profit=Decimal('60000'),  # 100000 - 40000
            gross_margin=Decimal('0.6'),
            operating_profit=Decimal('25000'),  # 60000 - 35000
            operating_margin=Decimal('0.25')
        )

        income_statement = IncomeStatement(
            period=period,
            revenue=revenue,
            costs=costs,
            expenses=expenses,
            metrics=metrics
        )

        assert income_statement.revenue.total_revenue == Decimal('100000')
        assert income_statement.metrics.gross_profit == Decimal('60000')


class TestValidationRules:
    """Test individual validation rules."""

    def setup_method(self):
        """Set up test fixtures."""
        self.period = FinancialPeriod(
            period_id="test-period",
            period_type=PeriodType.MONTHLY
        )

    def create_sample_income_statement(self, **overrides):
        """Create a sample income statement for testing."""
        defaults = {
            'total_revenue': Decimal('100000'),
            'food_revenue': Decimal('80000'),
            'beverage_revenue': Decimal('20000'),
            'total_cogs': Decimal('40000'),
            'food_cost': Decimal('32000'),
            'beverage_cost': Decimal('8000'),
            'total_operating_expenses': Decimal('35000'),
            'labor_cost': Decimal('25000'),
            'gross_margin': Decimal('0.6'),
            'food_cost_ratio': Decimal('0.4'),  # food_cost / food_revenue
            'labor_cost_ratio': Decimal('0.25'),
            'prime_cost_ratio': Decimal('0.65')
        }
        defaults.update(overrides)

        revenue = RevenueBreakdown(
            total_revenue=defaults['total_revenue'],
            food_revenue=defaults['food_revenue'],
            beverage_revenue=defaults['beverage_revenue']
        )

        costs = CostBreakdown(
            total_cogs=defaults['total_cogs'],
            food_cost=defaults['food_cost'],
            beverage_cost=defaults['beverage_cost']
        )

        expenses = ExpenseBreakdown(
            total_operating_expenses=defaults['total_operating_expenses'],
            labor_cost=defaults['labor_cost']
        )

        metrics = ProfitMetrics(
            gross_profit=defaults['total_revenue'] - defaults['total_cogs'],
            gross_margin=defaults['gross_margin'],
            operating_profit=defaults['total_revenue'] - defaults['total_cogs'] - defaults['total_operating_expenses'],
            operating_margin=(defaults['total_revenue'] - defaults['total_cogs'] - defaults['total_operating_expenses']) / defaults['total_revenue'],
            food_cost_ratio=defaults['food_cost_ratio'],
            labor_cost_ratio=defaults['labor_cost_ratio'],
            prime_cost_ratio=defaults['prime_cost_ratio']
        )

        return IncomeStatement(
            period=self.period,
            revenue=revenue,
            costs=costs,
            expenses=expenses,
            metrics=metrics
        )

    def test_restaurant_margin_rule_normal(self):
        """Test margin rule with normal restaurant margins."""
        rule = RestaurantMarginRule()
        income_statement = self.create_sample_income_statement(gross_margin=Decimal('0.65'))

        issues = rule.validate(income_statement)
        assert len(issues) == 0  # No issues for normal margin

    def test_restaurant_margin_rule_low_margin(self):
        """Test margin rule with low margin."""
        rule = RestaurantMarginRule()
        income_statement = self.create_sample_income_statement(gross_margin=Decimal('0.40'))

        issues = rule.validate(income_statement)
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "critically low" in issues[0].message

    def test_food_cost_ratio_rule_high_cost(self):
        """Test food cost ratio rule with high cost."""
        rule = FoodCostRatioRule()
        income_statement = self.create_sample_income_statement(food_cost_ratio=Decimal('0.50'))

        issues = rule.validate(income_statement)
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "critically high" in issues[0].message

    def test_labor_cost_ratio_rule_normal(self):
        """Test labor cost rule with normal ratio."""
        rule = LaborCostRatioRule()
        income_statement = self.create_sample_income_statement(labor_cost_ratio=Decimal('0.25'))

        issues = rule.validate(income_statement)
        assert len(issues) == 0  # No issues for normal labor cost


class TestRestaurantFinancialValidator:
    """Test the complete validation engine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RestaurantFinancialValidator()
        self.period = FinancialPeriod(
            period_id="test-period",
            period_type=PeriodType.MONTHLY
        )

    def create_healthy_restaurant(self):
        """Create a financially healthy restaurant for testing."""
        revenue = RevenueBreakdown(
            total_revenue=Decimal('100000'),
            food_revenue=Decimal('80000'),
            beverage_revenue=Decimal('15000'),
            dessert_revenue=Decimal('5000')
        )

        costs = CostBreakdown(
            total_cogs=Decimal('35000'),
            food_cost=Decimal('24000'),  # 30% of food revenue
            beverage_cost=Decimal('6000'),
            dessert_cost=Decimal('2000')
        )

        expenses = ExpenseBreakdown(
            total_operating_expenses=Decimal('40000'),
            labor_cost=Decimal('25000'),  # 25% of total revenue
            rent_expense=Decimal('10000'),
            utilities=Decimal('3000')
        )

        metrics = ProfitMetrics(
            gross_profit=Decimal('65000'),
            gross_margin=Decimal('0.65'),
            operating_profit=Decimal('25000'),
            operating_margin=Decimal('0.25'),
            food_cost_ratio=Decimal('0.30'),
            labor_cost_ratio=Decimal('0.25'),
            prime_cost_ratio=Decimal('0.60')
        )

        return IncomeStatement(
            period=self.period,
            revenue=revenue,
            costs=costs,
            expenses=expenses,
            metrics=metrics
        )

    def create_struggling_restaurant(self):
        """Create a struggling restaurant with validation issues."""
        revenue = RevenueBreakdown(
            total_revenue=Decimal('100000'),
            food_revenue=Decimal('80000'),
            beverage_revenue=Decimal('20000')
        )

        costs = CostBreakdown(
            total_cogs=Decimal('55000'),  # Very high costs
            food_cost=Decimal('40000'),  # 50% of food revenue - too high
            beverage_cost=Decimal('15000')
        )

        expenses = ExpenseBreakdown(
            total_operating_expenses=Decimal('35000'),
            labor_cost=Decimal('35000')  # 35% of revenue - too high
        )

        metrics = ProfitMetrics(
            gross_profit=Decimal('45000'),
            gross_margin=Decimal('0.45'),  # Low margin
            operating_profit=Decimal('10000'),
            operating_margin=Decimal('0.10'),
            food_cost_ratio=Decimal('0.50'),  # Too high
            labor_cost_ratio=Decimal('0.35'),  # Too high
            prime_cost_ratio=Decimal('0.90')  # Way too high
        )

        return IncomeStatement(
            period=self.period,
            revenue=revenue,
            costs=costs,
            expenses=expenses,
            metrics=metrics
        )

    def test_healthy_restaurant_validation(self):
        """Test validation of a healthy restaurant."""
        income_statement = self.create_healthy_restaurant()
        result = self.validator.validate(income_statement)

        assert result.is_valid == True
        assert result.errors_count == 0
        # May have some warnings for optimization opportunities

    def test_struggling_restaurant_validation(self):
        """Test validation of a struggling restaurant."""
        income_statement = self.create_struggling_restaurant()
        result = self.validator.validate(income_statement)

        assert result.is_valid == False
        assert result.errors_count > 0
        assert result.warnings_count >= 0

        # Check for specific issues
        all_codes = [issue.code for issue in result.issues]
        assert any("COST_001" in code for code in all_codes)  # High food cost
        assert any("LABOR_001" in code for code in all_codes)  # High labor cost


class TestValidationEngine:
    """Test the advanced validation engine with quality scoring."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ValidationEngine()

    def test_validation_with_quality_score(self):
        """Test validation with quality score calculation."""
        # Create a high-quality income statement
        period = FinancialPeriod(period_id="test", period_type=PeriodType.MONTHLY)

        revenue = RevenueBreakdown(
            total_revenue=Decimal('100000'),
            food_revenue=Decimal('80000'),
            beverage_revenue=Decimal('20000')
        )

        costs = CostBreakdown(
            total_cogs=Decimal('35000'),
            food_cost=Decimal('24000'),
            beverage_cost=Decimal('8000'),
            other_cost=Decimal('3000')  # Make components sum to total
        )

        expenses = ExpenseBreakdown(
            total_operating_expenses=Decimal('40000'),
            labor_cost=Decimal('25000')
        )

        metrics = ProfitMetrics(
            gross_profit=Decimal('65000'),
            gross_margin=Decimal('0.65'),
            operating_profit=Decimal('25000'),
            operating_margin=Decimal('0.25'),
            food_cost_ratio=Decimal('0.30'),
            labor_cost_ratio=Decimal('0.25'),
            prime_cost_ratio=Decimal('0.60')
        )

        income_statement = IncomeStatement(
            period=period,
            revenue=revenue,
            costs=costs,
            expenses=expenses,
            metrics=metrics
        )

        validation_result, quality_score = self.engine.validate_with_quality_score(income_statement)

        assert isinstance(validation_result, ValidationResult)
        assert isinstance(quality_score, DataQualityScore)
        assert 0 <= quality_score.overall_score <= 1
        assert quality_score.completeness_score > 0.4  # Should be reasonable for test data
        assert quality_score.accuracy_score > 0.8  # Should be high for valid data


class TestDataTransformer:
    """Test the data transformation pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = DataTransformer()

    def create_sample_parsed_data(self):
        """Create sample parsed data from Excel parser."""
        return {
            'parsing_status': 'success',
            'file_path': 'test.xlsx',
            'periods': ['1月', '占比', '2月'],
            'financial_data': {
                'operating_revenue': {
                    'chinese_term': '一、营业收入',
                    'values': {'1月': 100000, '占比': 1.0, '2月': 105000}
                },
                'food_revenue': {
                    'chinese_term': '食品收入',
                    'values': {'1月': 80000, '占比': 0.8, '2月': 84000}
                },
                'beverage_revenue': {
                    'chinese_term': '酒水收入',
                    'values': {'1月': 20000, '占比': 0.2, '2月': 21000}
                },
                'cogs': {
                    'chinese_term': '减:主营业务成本',
                    'values': {'1月': 35000, '占比': 0.35, '2月': 36000}
                },
                'food_cost': {
                    'chinese_term': '食品成本',
                    'values': {'1月': 24000, '占比': 0.24, '2月': 25000}
                },
                'labor_cost': {
                    'chinese_term': '其中：人工成本',
                    'values': {'1月': 25000, '占比': 0.25, '2月': 26000}
                }
            }
        }

    def test_successful_transformation(self):
        """Test successful data transformation."""
        parsed_data = self.create_sample_parsed_data()
        result = self.transformer.transform_parsed_data(parsed_data)

        assert result.success == True
        assert result.income_statement is not None
        assert result.validation_result is not None
        assert result.quality_score is not None

        # Check that data was mapped correctly
        income_statement = result.income_statement
        assert income_statement.revenue.total_revenue > 0
        assert income_statement.revenue.food_revenue > 0
        assert income_statement.costs.total_cogs > 0

    def test_transformation_with_missing_data(self):
        """Test transformation with incomplete data."""
        parsed_data = {
            'parsing_status': 'success',
            'periods': ['1月'],
            'financial_data': {
                'food_revenue': {
                    'chinese_term': '食品收入',
                    'values': {'1月': 50000}
                }
                # Missing total revenue and other fields
            }
        }

        result = self.transformer.transform_parsed_data(parsed_data)

        # Should still succeed but with warnings
        assert len(result.warnings) > 0
        assert result.income_statement is not None

    def test_transformation_error_handling(self):
        """Test transformation error handling."""
        # Invalid parsed data
        parsed_data = {
            'parsing_status': 'failed',
            'error': 'Test error'
        }

        result = self.transformer.transform_parsed_data(parsed_data)
        # Should handle gracefully without crashing


class TestIntegration:
    """Integration tests for the complete validation system."""

    def test_end_to_end_with_sample_data(self):
        """Test complete pipeline with sample Excel data."""
        # This test requires the sample Excel file to exist
        file_path = "data/sample_restaurant_income_2025.xlsx"

        if os.path.exists(file_path):
            transformer = DataTransformer()
            result = transformer.transform_excel_file(file_path)

            # Should complete without errors
            assert isinstance(result, TransformationResult)

            if result.success:
                assert result.income_statement is not None
                assert result.validation_result is not None
                assert result.quality_score is not None

                # Basic sanity checks
                assert result.income_statement.revenue.total_revenue > 0
                assert 0 <= result.quality_score.overall_score <= 1
        else:
            pytest.skip("Sample Excel file not found")

    def test_validation_pipeline_performance(self):
        """Test that validation pipeline performs reasonably."""
        import time

        transformer = DataTransformer()

        # Create sample data
        parsed_data = {
            'parsing_status': 'success',
            'periods': ['1月'],
            'financial_data': {
                'operating_revenue': {
                    'chinese_term': '一、营业收入',
                    'values': {'1月': 100000}
                },
                'food_revenue': {
                    'chinese_term': '食品收入',
                    'values': {'1月': 80000}
                },
                'cogs': {
                    'chinese_term': '减:主营业务成本',
                    'values': {'1月': 35000}
                }
            }
        }

        # Time the transformation
        start_time = time.time()
        result = transformer.transform_parsed_data(parsed_data)
        end_time = time.time()

        # Should complete quickly (under 1 second for simple data)
        assert (end_time - start_time) < 1.0
        assert result.success == True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])