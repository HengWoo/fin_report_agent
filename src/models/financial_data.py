"""
Pydantic models for standardized financial data structures.

This module defines the data models used throughout the financial reporting agent
to ensure consistent data types and validation.
"""

from typing import Dict, List, Optional, Union, Any
from decimal import Decimal
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
import logging

logger = logging.getLogger(__name__)


class PeriodType(str, Enum):
    """Types of financial periods."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class FinancialPeriod(BaseModel):
    """Represents a financial reporting period."""

    period_id: str = Field(..., description="Unique identifier for the period")
    period_type: PeriodType = Field(..., description="Type of period")
    start_date: Optional[date] = Field(None, description="Period start date")
    end_date: Optional[date] = Field(None, description="Period end date")
    chinese_label: Optional[str] = Field(None, description="Original Chinese period label")

    @field_validator('period_id')
    @classmethod
    def validate_period_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Period ID cannot be empty")
        return v.strip()

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
        return self


class RevenueBreakdown(BaseModel):
    """Revenue breakdown by category for restaurants."""

    total_revenue: Decimal = Field(0, ge=0, description="Total operating revenue")
    food_revenue: Decimal = Field(0, ge=0, description="Food sales revenue")
    beverage_revenue: Decimal = Field(0, ge=0, description="Beverage sales revenue")
    dessert_revenue: Decimal = Field(0, ge=0, description="Dessert/sweet sales revenue")
    other_revenue: Decimal = Field(0, ge=0, description="Other revenue sources")
    discounts: Decimal = Field(0, le=0, description="Customer discounts (negative)")

    @field_validator('discounts')
    @classmethod
    def validate_discounts(cls, v):
        if v > 0:
            logger.warning("Discounts should typically be negative values")
        return v

    @model_validator(mode='after')
    def validate_revenue_components(self):
        """Validate that component revenues sum to total (within tolerance)."""
        total = self.total_revenue
        components = (
            self.food_revenue +
            self.beverage_revenue +
            self.dessert_revenue +
            self.other_revenue +
            self.discounts
        )

        # Allow 1% tolerance for rounding differences
        tolerance = abs(total * Decimal('0.01'))
        if abs(total - components) > tolerance:
            logger.warning(
                f"Revenue components ({components}) don't sum to total ({total}). "
                f"Difference: {abs(total - components)}"
            )

        return self


class CostBreakdown(BaseModel):
    """Cost of goods sold breakdown."""

    total_cogs: Decimal = Field(0, ge=0, description="Total cost of goods sold")
    food_cost: Decimal = Field(0, ge=0, description="Food ingredient costs")
    beverage_cost: Decimal = Field(0, ge=0, description="Beverage costs")
    dessert_cost: Decimal = Field(0, ge=0, description="Dessert ingredient costs")
    other_cost: Decimal = Field(0, ge=0, description="Other direct costs")

    @model_validator(mode='after')
    def validate_cost_components(self):
        """Validate that component costs sum to total (within tolerance)."""
        total = self.total_cogs
        components = (
            self.food_cost +
            self.beverage_cost +
            self.dessert_cost +
            self.other_cost
        )

        tolerance = abs(total * Decimal('0.01'))
        if abs(total - components) > tolerance:
            logger.warning(
                f"Cost components ({components}) don't sum to total ({total}). "
                f"Difference: {abs(total - components)}"
            )

        return self


class ExpenseBreakdown(BaseModel):
    """Operating expense breakdown."""

    total_operating_expenses: Decimal = Field(0, ge=0, description="Total operating expenses")
    labor_cost: Decimal = Field(0, ge=0, description="Total labor costs")
    wages: Decimal = Field(0, ge=0, description="Employee wages")
    benefits: Decimal = Field(0, ge=0, description="Employee benefits and insurance")
    rent_expense: Decimal = Field(0, ge=0, description="Total rent expenses")
    storefront_rent: Decimal = Field(0, ge=0, description="Main store rent")
    dormitory_rent: Decimal = Field(0, ge=0, description="Employee housing rent")
    utilities: Decimal = Field(0, ge=0, description="Utilities and property management")
    marketing: Decimal = Field(0, ge=0, description="Marketing and advertising")
    other_expenses: Decimal = Field(0, ge=0, description="Other operating expenses")

    @model_validator(mode='after')
    def validate_components(self):
        """Validate labor and rent cost breakdowns."""
        # Validate labor cost breakdown
        if self.wages + self.benefits > 0:
            tolerance = abs(self.labor_cost * Decimal('0.01'))
            if abs(self.labor_cost - (self.wages + self.benefits)) > tolerance:
                logger.warning(
                    f"Labor components don't sum to total. "
                    f"Total: {self.labor_cost}, Wages: {self.wages}, Benefits: {self.benefits}"
                )

        # Validate rent expense breakdown
        if self.storefront_rent + self.dormitory_rent > 0:
            tolerance = abs(self.rent_expense * Decimal('0.01'))
            if abs(self.rent_expense - (self.storefront_rent + self.dormitory_rent)) > tolerance:
                logger.warning(
                    f"Rent components don't sum to total. "
                    f"Total: {self.rent_expense}, Storefront: {self.storefront_rent}, Dormitory: {self.dormitory_rent}"
                )

        return self


class ProfitMetrics(BaseModel):
    """Calculated profit metrics and ratios."""

    gross_profit: Decimal = Field(..., description="Revenue minus COGS")
    gross_margin: Decimal = Field(..., ge=0, le=1, description="Gross profit / Revenue")
    operating_profit: Decimal = Field(..., description="Gross profit minus operating expenses")
    operating_margin: Decimal = Field(..., ge=-1, le=1, description="Operating profit / Revenue")

    # Category-specific margins
    food_margin: Optional[Decimal] = Field(None, ge=0, le=1, description="Food gross margin")
    beverage_margin: Optional[Decimal] = Field(None, ge=0, le=1, description="Beverage gross margin")
    dessert_margin: Optional[Decimal] = Field(None, ge=0, le=1, description="Dessert gross margin")

    # Restaurant-specific ratios
    food_cost_ratio: Optional[Decimal] = Field(None, ge=0, le=1, description="Food cost / Food revenue")
    labor_cost_ratio: Optional[Decimal] = Field(None, ge=0, le=1, description="Labor cost / Total revenue")
    prime_cost_ratio: Optional[Decimal] = Field(None, ge=0, le=1, description="(COGS + Labor) / Revenue")

    @field_validator('gross_margin', 'operating_margin', 'food_margin', 'beverage_margin', 'dessert_margin')
    @classmethod
    def validate_margins(cls, v, info):
        """Validate margin ranges for restaurants."""
        if v is not None:
            field_name = info.field_name
            if field_name == 'gross_margin' and (v < 0.3 or v > 0.9):
                logger.warning(f"Gross margin {v:.1%} is outside typical restaurant range (30-90%)")
            elif field_name in ['food_margin', 'beverage_margin', 'dessert_margin'] and (v < 0.2 or v > 0.8):
                logger.warning(f"{field_name} {v:.1%} is outside typical range (20-80%)")
        return v

    @field_validator('food_cost_ratio', 'labor_cost_ratio', 'prime_cost_ratio')
    @classmethod
    def validate_cost_ratios(cls, v, info):
        """Validate cost ratio ranges for restaurants."""
        if v is not None:
            field_name = info.field_name
            if field_name == 'food_cost_ratio' and (v < 0.15 or v > 0.45):
                logger.warning(f"Food cost ratio {v:.1%} is outside typical range (15-45%)")
            elif field_name == 'labor_cost_ratio' and (v < 0.15 or v > 0.35):
                logger.warning(f"Labor cost ratio {v:.1%} is outside typical range (15-35%)")
            elif field_name == 'prime_cost_ratio' and (v < 0.45 or v > 0.75):
                logger.warning(f"Prime cost ratio {v:.1%} is outside typical range (45-75%)")
        return v


class IncomeStatement(BaseModel):
    """Complete income statement for a restaurant."""

    period: FinancialPeriod = Field(..., description="Financial period")
    revenue: RevenueBreakdown = Field(..., description="Revenue breakdown")
    costs: CostBreakdown = Field(..., description="Cost breakdown")
    expenses: ExpenseBreakdown = Field(..., description="Expense breakdown")
    metrics: ProfitMetrics = Field(..., description="Calculated metrics")

    # Metadata
    restaurant_name: Optional[str] = Field(None, description="Restaurant name")
    currency: str = Field("CNY", description="Currency code")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Original parsed data")

    @model_validator(mode='after')
    def validate_financial_consistency(self):
        """Validate overall financial statement consistency."""
        if all([self.revenue, self.costs, self.metrics]):
            # Validate gross profit calculation
            calculated_gross_profit = self.revenue.total_revenue - self.costs.total_cogs
            tolerance = abs(calculated_gross_profit * Decimal('0.01'))

            if abs(self.metrics.gross_profit - calculated_gross_profit) > tolerance:
                logger.warning(
                    f"Gross profit calculation inconsistent. "
                    f"Calculated: {calculated_gross_profit}, Reported: {self.metrics.gross_profit}"
                )

        return self


class ValidationIssue(BaseModel):
    """Represents a validation issue found in financial data."""

    severity: ValidationSeverity = Field(..., description="Issue severity")
    code: str = Field(..., description="Validation rule code")
    message: str = Field(..., description="Human-readable message")
    field: Optional[str] = Field(None, description="Field that failed validation")
    value: Optional[Any] = Field(None, description="Value that caused the issue")
    suggestion: Optional[str] = Field(None, description="Suggested fix")


class ValidationResult(BaseModel):
    """Result of financial data validation."""

    is_valid: bool = Field(..., description="Overall validation status")
    issues: List[ValidationIssue] = Field(default_factory=list, description="List of validation issues")
    warnings_count: int = Field(0, description="Number of warnings")
    errors_count: int = Field(0, description="Number of errors")

    @model_validator(mode='after')
    def calculate_counts(self):
        """Calculate issue counts."""
        warnings = sum(1 for issue in self.issues if issue.severity == ValidationSeverity.WARNING)
        errors = sum(1 for issue in self.issues if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL])

        self.warnings_count = warnings
        self.errors_count = errors
        self.is_valid = errors == 0

        return self


class DataQualityScore(BaseModel):
    """Data quality assessment score."""

    overall_score: float = Field(..., ge=0, le=1, description="Overall quality score (0-1)")
    completeness_score: float = Field(..., ge=0, le=1, description="Data completeness score")
    accuracy_score: float = Field(..., ge=0, le=1, description="Data accuracy score")
    consistency_score: float = Field(..., ge=0, le=1, description="Data consistency score")

    # Detailed scores
    revenue_quality: float = Field(..., ge=0, le=1, description="Revenue data quality")
    cost_quality: float = Field(..., ge=0, le=1, description="Cost data quality")
    expense_quality: float = Field(..., ge=0, le=1, description="Expense data quality")

    # Quality indicators
    missing_fields: List[str] = Field(default_factory=list, description="List of missing required fields")
    suspicious_values: List[str] = Field(default_factory=list, description="List of suspicious values")
    calculation_errors: List[str] = Field(default_factory=list, description="List of calculation errors")

    @field_validator('overall_score')
    @classmethod
    def validate_overall_score(cls, v, info):
        """Validate overall score is reasonable."""
        # Note: In Pydantic V2, we can't access other fields during field validation
        # So we'll just do basic range validation here
        if not (0 <= v <= 1):
            raise ValueError("Overall score must be between 0 and 1")
        return v


# Utility functions for creating models from parsed data

def create_financial_period(period_str: str, chinese_label: str = None) -> FinancialPeriod:
    """Create a FinancialPeriod from a period string."""
    period_type = PeriodType.CUSTOM

    if "月" in period_str:
        period_type = PeriodType.MONTHLY
    elif "季" in period_str or "Q" in period_str:
        period_type = PeriodType.QUARTERLY
    elif "年" in period_str:
        period_type = PeriodType.ANNUAL

    return FinancialPeriod(
        period_id=period_str,
        period_type=period_type,
        chinese_label=chinese_label or period_str
    )


def create_income_statement_from_parsed_data(parsed_data: Dict[str, Any]) -> IncomeStatement:
    """Create an IncomeStatement from parsed Excel data."""
    # This is a placeholder - implementation would depend on the specific
    # structure of the parsed data from the Excel parser

    # Extract period information
    periods = parsed_data.get('periods', [])
    main_period = periods[0] if periods else "Unknown"
    period = create_financial_period(main_period)

    # Create empty structures - these would be populated from actual data
    revenue = RevenueBreakdown()
    costs = CostBreakdown()
    expenses = ExpenseBreakdown()

    # Calculate basic metrics
    gross_profit = revenue.total_revenue - costs.total_cogs
    gross_margin = gross_profit / revenue.total_revenue if revenue.total_revenue > 0 else Decimal(0)
    operating_profit = gross_profit - expenses.total_operating_expenses
    operating_margin = operating_profit / revenue.total_revenue if revenue.total_revenue > 0 else Decimal(0)

    metrics = ProfitMetrics(
        gross_profit=gross_profit,
        gross_margin=gross_margin,
        operating_profit=operating_profit,
        operating_margin=operating_margin
    )

    return IncomeStatement(
        period=period,
        revenue=revenue,
        costs=costs,
        expenses=expenses,
        metrics=metrics,
        raw_data=parsed_data
    )