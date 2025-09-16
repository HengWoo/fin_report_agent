"""
Data transformation module for converting parsed Excel data to validated financial models.

This module bridges the gap between raw parsed data and structured financial models,
handling data mapping, calculation, and error recovery.
"""

from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, InvalidOperation
import logging
from datetime import datetime

from ..models.financial_data import (
    IncomeStatement,
    RevenueBreakdown,
    CostBreakdown,
    ExpenseBreakdown,
    ProfitMetrics,
    FinancialPeriod,
    PeriodType,
    ValidationResult,
    DataQualityScore
)
from ..validators.restaurant_validator import ValidationEngine
from ..parsers.chinese_excel_parser import ChineseExcelParser

logger = logging.getLogger(__name__)


class TransformationResult:
    """Result of data transformation process."""

    def __init__(
        self,
        income_statement: Optional[IncomeStatement] = None,
        validation_result: Optional[ValidationResult] = None,
        quality_score: Optional[DataQualityScore] = None,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ):
        self.income_statement = income_statement
        self.validation_result = validation_result
        self.quality_score = quality_score
        self.errors = errors or []
        self.warnings = warnings or []
        self.success = income_statement is not None and len(self.errors) == 0

    def __str__(self):
        if self.success:
            quality = f"{self.quality_score.overall_score:.1%}" if self.quality_score else "Unknown"
            return f"Transformation successful (Quality: {quality})"
        else:
            return f"Transformation failed: {'; '.join(self.errors)}"


class DataTransformer:
    """
    Transform parsed Excel data into validated financial models.

    This class handles the complex mapping between Chinese financial terms
    and standardized financial statement structures, with comprehensive
    error handling and data quality assessment.
    """

    def __init__(self):
        self.validation_engine = ValidationEngine()
        self.chinese_to_english = {
            # Revenue mappings
            "一、营业收入": "total_revenue",
            "营业收入": "total_revenue",
            "食品收入": "food_revenue",
            "酒水收入": "beverage_revenue",
            "甜品/糖水收入": "dessert_revenue",
            "甜品收入": "dessert_revenue",
            "糖水收入": "dessert_revenue",
            "其他收入": "other_revenue",
            "其他（碳餐盒等）收入": "other_revenue",
            "折扣": "discounts",

            # Cost mappings
            "减:主营业务成本": "total_cogs",
            "主营业务成本": "total_cogs",
            "食品成本": "food_cost",
            "酒水成本": "beverage_cost",
            "甜品/糖水成本": "dessert_cost",
            "甜品成本": "dessert_cost",

            # Expense mappings
            "四、营业费用": "total_operating_expenses",
            "营业费用": "total_operating_expenses",
            "其中：人工成本": "labor_cost",
            "人工成本": "labor_cost",
            "工资": "wages",
            "员工奖励/奖金": "bonuses",
            "社保/商业保险": "benefits",
            "其中：租赁费用": "rent_expense",
            "租赁费用": "rent_expense",
            "门面房租": "storefront_rent",
            "宿舍租金": "dormitory_rent",
            "物业费/垃圾清运": "utilities",
            "物业费": "utilities",

            # Calculated metrics
            "二、毛利": "gross_profit",
            "毛利": "gross_profit",
            "毛利率": "gross_margin",
            "食品毛利率：": "food_margin",
            "酒水毛利率：": "beverage_margin",
            "甜品/糖水毛利率：": "dessert_margin"
        }

    def transform_parsed_data(self, parsed_data: Dict[str, Any]) -> TransformationResult:
        """
        Transform parsed Excel data into a validated IncomeStatement.

        Args:
            parsed_data: Output from ChineseExcelParser

        Returns:
            TransformationResult with income statement and validation results
        """
        errors = []
        warnings = []

        try:
            # Extract financial period
            period = self._extract_period(parsed_data)

            # Transform financial data
            revenue = self._extract_revenue(parsed_data, errors, warnings)
            costs = self._extract_costs(parsed_data, errors, warnings)
            expenses = self._extract_expenses(parsed_data, errors, warnings)

            # Calculate metrics
            metrics = self._calculate_metrics(revenue, costs, expenses, errors, warnings)

            # Create income statement
            income_statement = IncomeStatement(
                period=period,
                revenue=revenue,
                costs=costs,
                expenses=expenses,
                metrics=metrics,
                raw_data=parsed_data
            )

            # Validate and score
            validation_result, quality_score = self.validation_engine.validate_with_quality_score(income_statement)

            return TransformationResult(
                income_statement=income_statement,
                validation_result=validation_result,
                quality_score=quality_score,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            logger.error(f"Transformation failed: {str(e)}")
            errors.append(f"Transformation error: {str(e)}")
            return TransformationResult(errors=errors, warnings=warnings)

    def _extract_period(self, parsed_data: Dict[str, Any]) -> FinancialPeriod:
        """Extract and parse the financial period."""
        periods = parsed_data.get('periods', [])

        if not periods:
            return FinancialPeriod(
                period_id="unknown",
                period_type=PeriodType.CUSTOM,
                chinese_label="未知期间"
            )

        # Use the first non-percentage period as the main period
        main_period = None
        for period in periods:
            if "占比" not in period and period.strip():
                main_period = period
                break

        if not main_period:
            main_period = periods[0]

        # Determine period type
        period_type = PeriodType.CUSTOM
        if "月" in main_period:
            period_type = PeriodType.MONTHLY
        elif "季" in main_period or "Q" in main_period:
            period_type = PeriodType.QUARTERLY
        elif "年" in main_period:
            period_type = PeriodType.ANNUAL

        return FinancialPeriod(
            period_id=main_period,
            period_type=period_type,
            chinese_label=main_period
        )

    def _extract_revenue(self, parsed_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> RevenueBreakdown:
        """Extract and validate revenue data."""
        financial_data = parsed_data.get('financial_data', {})

        revenue_data = {}

        # Map Chinese terms to revenue fields
        for chinese_term, data in financial_data.items():
            english_field = self.chinese_to_english.get(data.get('chinese_term', ''))
            if english_field in ['total_revenue', 'food_revenue', 'beverage_revenue', 'dessert_revenue', 'other_revenue', 'discounts']:
                # Get the first numeric value from the data
                values = data.get('values', {})
                for period_key, value in values.items():
                    if isinstance(value, (int, float)) and "占比" not in period_key:
                        try:
                            revenue_data[english_field] = Decimal(str(value))
                            break
                        except (InvalidOperation, ValueError) as e:
                            warnings.append(f"Could not convert {chinese_term} value {value} to Decimal: {e}")

        # Handle missing or zero total revenue
        if 'total_revenue' not in revenue_data or revenue_data['total_revenue'] <= 0:
            # Try to calculate from components
            component_sum = (
                revenue_data.get('food_revenue', Decimal('0')) +
                revenue_data.get('beverage_revenue', Decimal('0')) +
                revenue_data.get('dessert_revenue', Decimal('0')) +
                revenue_data.get('other_revenue', Decimal('0')) +
                revenue_data.get('discounts', Decimal('0'))
            )

            if component_sum > 0:
                revenue_data['total_revenue'] = component_sum
                warnings.append("Total revenue calculated from components")
            else:
                errors.append("No valid revenue data found")
                revenue_data['total_revenue'] = Decimal('0')

        return RevenueBreakdown(
            total_revenue=revenue_data.get('total_revenue', Decimal('0')),
            food_revenue=revenue_data.get('food_revenue', Decimal('0')),
            beverage_revenue=revenue_data.get('beverage_revenue', Decimal('0')),
            dessert_revenue=revenue_data.get('dessert_revenue', Decimal('0')),
            other_revenue=revenue_data.get('other_revenue', Decimal('0')),
            discounts=revenue_data.get('discounts', Decimal('0'))
        )

    def _extract_costs(self, parsed_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> CostBreakdown:
        """Extract and validate cost data."""
        financial_data = parsed_data.get('financial_data', {})

        cost_data = {}

        # Map Chinese terms to cost fields
        for chinese_term, data in financial_data.items():
            english_field = self.chinese_to_english.get(data.get('chinese_term', ''))
            if english_field in ['total_cogs', 'food_cost', 'beverage_cost', 'dessert_cost']:
                values = data.get('values', {})
                for period_key, value in values.items():
                    if isinstance(value, (int, float)) and "占比" not in period_key:
                        try:
                            cost_data[english_field] = Decimal(str(value))
                            break
                        except (InvalidOperation, ValueError) as e:
                            warnings.append(f"Could not convert {chinese_term} value {value} to Decimal: {e}")

        # Handle missing total COGS
        if 'total_cogs' not in cost_data:
            component_sum = (
                cost_data.get('food_cost', Decimal('0')) +
                cost_data.get('beverage_cost', Decimal('0')) +
                cost_data.get('dessert_cost', Decimal('0'))
            )

            if component_sum > 0:
                cost_data['total_cogs'] = component_sum
                warnings.append("Total COGS calculated from components")

        return CostBreakdown(
            total_cogs=cost_data.get('total_cogs', Decimal('0')),
            food_cost=cost_data.get('food_cost', Decimal('0')),
            beverage_cost=cost_data.get('beverage_cost', Decimal('0')),
            dessert_cost=cost_data.get('dessert_cost', Decimal('0')),
            other_cost=Decimal('0')  # Not typically separated in Chinese statements
        )

    def _extract_expenses(self, parsed_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> ExpenseBreakdown:
        """Extract and validate expense data."""
        financial_data = parsed_data.get('financial_data', {})

        expense_data = {}

        # Map Chinese terms to expense fields
        expense_fields = [
            'total_operating_expenses', 'labor_cost', 'wages', 'benefits',
            'rent_expense', 'storefront_rent', 'dormitory_rent', 'utilities'
        ]

        for chinese_term, data in financial_data.items():
            english_field = self.chinese_to_english.get(data.get('chinese_term', ''))
            if english_field in expense_fields:
                values = data.get('values', {})
                for period_key, value in values.items():
                    if isinstance(value, (int, float)) and "占比" not in period_key:
                        try:
                            expense_data[english_field] = Decimal(str(value))
                            break
                        except (InvalidOperation, ValueError) as e:
                            warnings.append(f"Could not convert {chinese_term} value {value} to Decimal: {e}")

        return ExpenseBreakdown(
            total_operating_expenses=expense_data.get('total_operating_expenses', Decimal('0')),
            labor_cost=expense_data.get('labor_cost', Decimal('0')),
            wages=expense_data.get('wages', Decimal('0')),
            benefits=expense_data.get('benefits', Decimal('0')),
            rent_expense=expense_data.get('rent_expense', Decimal('0')),
            storefront_rent=expense_data.get('storefront_rent', Decimal('0')),
            dormitory_rent=expense_data.get('dormitory_rent', Decimal('0')),
            utilities=expense_data.get('utilities', Decimal('0')),
            marketing=Decimal('0'),  # Not typically separated
            other_expenses=Decimal('0')
        )

    def _calculate_metrics(
        self,
        revenue: RevenueBreakdown,
        costs: CostBreakdown,
        expenses: ExpenseBreakdown,
        errors: List[str],
        warnings: List[str]
    ) -> ProfitMetrics:
        """Calculate financial metrics with error handling."""

        try:
            # Basic profit calculations
            gross_profit = revenue.total_revenue - costs.total_cogs
            operating_profit = gross_profit - expenses.total_operating_expenses

            # Margin calculations
            gross_margin = Decimal('0')
            operating_margin = Decimal('0')

            if revenue.total_revenue > 0:
                gross_margin = gross_profit / revenue.total_revenue
                operating_margin = operating_profit / revenue.total_revenue

            # Category-specific margins
            food_margin = None
            if revenue.food_revenue > 0 and costs.food_cost >= 0:
                food_margin = (revenue.food_revenue - costs.food_cost) / revenue.food_revenue

            beverage_margin = None
            if revenue.beverage_revenue > 0 and costs.beverage_cost >= 0:
                beverage_margin = (revenue.beverage_revenue - costs.beverage_cost) / revenue.beverage_revenue

            dessert_margin = None
            if revenue.dessert_revenue > 0 and costs.dessert_cost >= 0:
                dessert_margin = (revenue.dessert_revenue - costs.dessert_cost) / revenue.dessert_revenue

            # Cost ratios
            food_cost_ratio = None
            if revenue.food_revenue > 0:
                food_cost_ratio = costs.food_cost / revenue.food_revenue

            labor_cost_ratio = None
            if revenue.total_revenue > 0:
                labor_cost_ratio = expenses.labor_cost / revenue.total_revenue

            prime_cost_ratio = None
            if revenue.total_revenue > 0:
                prime_cost_ratio = (costs.total_cogs + expenses.labor_cost) / revenue.total_revenue

            return ProfitMetrics(
                gross_profit=gross_profit,
                gross_margin=gross_margin,
                operating_profit=operating_profit,
                operating_margin=operating_margin,
                food_margin=food_margin,
                beverage_margin=beverage_margin,
                dessert_margin=dessert_margin,
                food_cost_ratio=food_cost_ratio,
                labor_cost_ratio=labor_cost_ratio,
                prime_cost_ratio=prime_cost_ratio
            )

        except Exception as e:
            errors.append(f"Error calculating metrics: {str(e)}")
            # Return basic metrics with zeros
            return ProfitMetrics(
                gross_profit=Decimal('0'),
                gross_margin=Decimal('0'),
                operating_profit=Decimal('0'),
                operating_margin=Decimal('0')
            )

    def transform_excel_file(self, file_path: str) -> TransformationResult:
        """
        Complete transformation pipeline from Excel file to validated income statement.

        Args:
            file_path: Path to Excel file

        Returns:
            TransformationResult with complete analysis
        """
        try:
            # Parse Excel file
            parser = ChineseExcelParser()
            parsed_data = parser.parse_income_statement(file_path)

            if parsed_data.get('parsing_status') != 'success':
                return TransformationResult(
                    errors=[f"Excel parsing failed: {parsed_data.get('error', 'Unknown error')}"]
                )

            # Transform to structured data
            return self.transform_parsed_data(parsed_data)

        except Exception as e:
            logger.error(f"Excel transformation failed: {str(e)}")
            return TransformationResult(errors=[f"Excel transformation failed: {str(e)}"])


# Utility function for easy integration
def analyze_restaurant_excel(file_path: str) -> TransformationResult:
    """
    One-stop function to analyze a Chinese restaurant Excel file.

    Args:
        file_path: Path to Excel file

    Returns:
        Complete transformation result with validation and quality scores
    """
    transformer = DataTransformer()
    return transformer.transform_excel_file(file_path)