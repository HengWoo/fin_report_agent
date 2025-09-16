"""
Restaurant-specific financial validation rules and engine.

This module implements validation rules specific to restaurant operations,
including industry benchmarks and business logic validation.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple
from decimal import Decimal
from abc import ABC, abstractmethod
import logging

from ..models.financial_data import (
    IncomeStatement,
    RevenueBreakdown,
    CostBreakdown,
    ExpenseBreakdown,
    ProfitMetrics,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    DataQualityScore
)

logger = logging.getLogger(__name__)


class ValidationRule(ABC):
    """Abstract base class for validation rules."""

    def __init__(self, code: str, description: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.code = code
        self.description = description
        self.severity = severity

    @abstractmethod
    def validate(self, income_statement: IncomeStatement) -> List[ValidationIssue]:
        """Execute the validation rule."""
        pass


class RestaurantMarginRule(ValidationRule):
    """Validate restaurant profit margins against industry benchmarks."""

    def __init__(self):
        super().__init__(
            code="MARGIN_001",
            description="Validate gross margins are within restaurant industry ranges",
            severity=ValidationSeverity.WARNING
        )

    def validate(self, income_statement: IncomeStatement) -> List[ValidationIssue]:
        issues = []
        metrics = income_statement.metrics

        # Gross margin should be 55-75% for most restaurants
        if metrics.gross_margin < Decimal('0.45'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code=f"{self.code}_LOW_GROSS",
                message=f"Gross margin {metrics.gross_margin:.1%} is critically low for restaurants",
                field="gross_margin",
                value=float(metrics.gross_margin),
                suggestion="Review pricing strategy and cost controls"
            ))
        elif metrics.gross_margin < Decimal('0.55'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code=f"{self.code}_BELOW_BENCHMARK",
                message=f"Gross margin {metrics.gross_margin:.1%} is below industry average (55-75%)",
                field="gross_margin",
                value=float(metrics.gross_margin),
                suggestion="Consider optimizing menu pricing and ingredient costs"
            ))
        elif metrics.gross_margin > Decimal('0.85'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code=f"{self.code}_UNUSUALLY_HIGH",
                message=f"Gross margin {metrics.gross_margin:.1%} is unusually high",
                field="gross_margin",
                value=float(metrics.gross_margin),
                suggestion="Verify cost calculations and pricing data"
            ))

        return issues


class FoodCostRatioRule(ValidationRule):
    """Validate food cost ratios."""

    def __init__(self):
        super().__init__(
            code="COST_001",
            description="Validate food cost ratios against industry standards",
            severity=ValidationSeverity.WARNING
        )

    def validate(self, income_statement: IncomeStatement) -> List[ValidationIssue]:
        issues = []
        metrics = income_statement.metrics

        if metrics.food_cost_ratio is not None:
            # Food cost should be 25-35% for most restaurants
            if metrics.food_cost_ratio > Decimal('0.45'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code=f"{self.code}_HIGH_FOOD_COST",
                    message=f"Food cost ratio {metrics.food_cost_ratio:.1%} is critically high",
                    field="food_cost_ratio",
                    value=float(metrics.food_cost_ratio),
                    suggestion="Review portion control, waste management, and supplier costs"
                ))
            elif metrics.food_cost_ratio > Decimal('0.35'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code=f"{self.code}_ABOVE_BENCHMARK",
                    message=f"Food cost ratio {metrics.food_cost_ratio:.1%} is above industry average (25-35%)",
                    field="food_cost_ratio",
                    value=float(metrics.food_cost_ratio),
                    suggestion="Consider menu engineering and cost optimization"
                ))
            elif metrics.food_cost_ratio < Decimal('0.15'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code=f"{self.code}_UNUSUALLY_LOW",
                    message=f"Food cost ratio {metrics.food_cost_ratio:.1%} is unusually low",
                    field="food_cost_ratio",
                    value=float(metrics.food_cost_ratio),
                    suggestion="Verify cost allocation and inventory valuation"
                ))

        return issues


class LaborCostRatioRule(ValidationRule):
    """Validate labor cost ratios."""

    def __init__(self):
        super().__init__(
            code="LABOR_001",
            description="Validate labor cost ratios against industry standards",
            severity=ValidationSeverity.WARNING
        )

    def validate(self, income_statement: IncomeStatement) -> List[ValidationIssue]:
        issues = []
        metrics = income_statement.metrics

        if metrics.labor_cost_ratio is not None:
            # Labor cost should be 20-30% for most restaurants
            if metrics.labor_cost_ratio > Decimal('0.40'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code=f"{self.code}_HIGH_LABOR_COST",
                    message=f"Labor cost ratio {metrics.labor_cost_ratio:.1%} is critically high",
                    field="labor_cost_ratio",
                    value=float(metrics.labor_cost_ratio),
                    suggestion="Review staffing levels and labor efficiency"
                ))
            elif metrics.labor_cost_ratio > Decimal('0.30'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code=f"{self.code}_ABOVE_BENCHMARK",
                    message=f"Labor cost ratio {metrics.labor_cost_ratio:.1%} is above industry average (20-30%)",
                    field="labor_cost_ratio",
                    value=float(metrics.labor_cost_ratio),
                    suggestion="Consider optimizing schedules and productivity"
                ))

        return issues


class PrimeCostRule(ValidationRule):
    """Validate prime cost (COGS + Labor) ratios."""

    def __init__(self):
        super().__init__(
            code="PRIME_001",
            description="Validate prime cost ratios for operational efficiency",
            severity=ValidationSeverity.WARNING
        )

    def validate(self, income_statement: IncomeStatement) -> List[ValidationIssue]:
        issues = []
        metrics = income_statement.metrics

        if metrics.prime_cost_ratio is not None:
            # Prime cost should be 50-65% for healthy restaurants
            if metrics.prime_cost_ratio > Decimal('0.75'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code=f"{self.code}_HIGH_PRIME_COST",
                    message=f"Prime cost ratio {metrics.prime_cost_ratio:.1%} is critically high",
                    field="prime_cost_ratio",
                    value=float(metrics.prime_cost_ratio),
                    suggestion="Urgent review of both food costs and labor efficiency needed"
                ))
            elif metrics.prime_cost_ratio > Decimal('0.65'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code=f"{self.code}_ABOVE_BENCHMARK",
                    message=f"Prime cost ratio {metrics.prime_cost_ratio:.1%} is above healthy range (50-65%)",
                    field="prime_cost_ratio",
                    value=float(metrics.prime_cost_ratio),
                    suggestion="Focus on optimizing both food costs and labor costs"
                ))

        return issues


class RevenueConsistencyRule(ValidationRule):
    """Validate revenue component consistency."""

    def __init__(self):
        super().__init__(
            code="REV_001",
            description="Validate revenue components sum correctly",
            severity=ValidationSeverity.ERROR
        )

    def validate(self, income_statement: IncomeStatement) -> List[ValidationIssue]:
        issues = []
        revenue = income_statement.revenue

        # Calculate component sum
        component_sum = (
            revenue.food_revenue +
            revenue.beverage_revenue +
            revenue.dessert_revenue +
            revenue.other_revenue +
            revenue.discounts
        )

        # Allow 1% tolerance for rounding
        tolerance = abs(revenue.total_revenue * Decimal('0.01'))
        difference = abs(revenue.total_revenue - component_sum)

        if difference > tolerance:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code=f"{self.code}_COMPONENT_MISMATCH",
                message=f"Revenue components don't sum to total. Difference: {difference}",
                field="total_revenue",
                value=float(difference),
                suggestion="Check revenue allocation and ensure all components are captured"
            ))

        # Check for negative revenues (except discounts)
        if revenue.food_revenue < 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code=f"{self.code}_NEGATIVE_FOOD_REV",
                message="Food revenue cannot be negative",
                field="food_revenue",
                value=float(revenue.food_revenue)
            ))

        if revenue.beverage_revenue < 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code=f"{self.code}_NEGATIVE_BEV_REV",
                message="Beverage revenue cannot be negative",
                field="beverage_revenue",
                value=float(revenue.beverage_revenue)
            ))

        # Check discount reasonableness
        if revenue.discounts < 0 and abs(revenue.discounts) > revenue.total_revenue * Decimal('0.3'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code=f"{self.code}_HIGH_DISCOUNTS",
                message=f"Discounts {abs(revenue.discounts / revenue.total_revenue):.1%} are unusually high",
                field="discounts",
                value=float(revenue.discounts),
                suggestion="Review discount policies and promotional strategies"
            ))

        return issues


class BusinessLogicRule(ValidationRule):
    """Validate basic business logic constraints."""

    def __init__(self):
        super().__init__(
            code="LOGIC_001",
            description="Validate basic business logic constraints",
            severity=ValidationSeverity.ERROR
        )

    def validate(self, income_statement: IncomeStatement) -> List[ValidationIssue]:
        issues = []

        # Revenue must be positive for operating business
        if income_statement.revenue.total_revenue <= 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code=f"{self.code}_NO_REVENUE",
                message="Total revenue must be positive for operating business",
                field="total_revenue",
                value=float(income_statement.revenue.total_revenue)
            ))

        # COGS cannot exceed revenue (would indicate data error)
        if income_statement.costs.total_cogs > income_statement.revenue.total_revenue:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code=f"{self.code}_COGS_EXCEEDS_REVENUE",
                message="Cost of goods sold cannot exceed revenue",
                field="total_cogs",
                value=float(income_statement.costs.total_cogs),
                suggestion="Verify cost allocation and inventory calculations"
            ))

        # Check for reasonable expense ratios
        if (income_statement.expenses.total_operating_expenses >
            income_statement.revenue.total_revenue * Decimal('0.8')):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code=f"{self.code}_HIGH_EXPENSES",
                message="Operating expenses exceed 80% of revenue",
                field="total_operating_expenses",
                value=float(income_statement.expenses.total_operating_expenses),
                suggestion="Review expense management and operational efficiency"
            ))

        return issues


class RestaurantFinancialValidator:
    """Main validator for restaurant financial data."""

    def __init__(self):
        self.rules = [
            RestaurantMarginRule(),
            FoodCostRatioRule(),
            LaborCostRatioRule(),
            PrimeCostRule(),
            RevenueConsistencyRule(),
            BusinessLogicRule()
        ]

    def validate(self, income_statement: IncomeStatement) -> ValidationResult:
        """
        Run all validation rules against the income statement.

        Args:
            income_statement: The financial data to validate

        Returns:
            ValidationResult with all issues found
        """
        all_issues = []

        for rule in self.rules:
            try:
                issues = rule.validate(income_statement)
                all_issues.extend(issues)
            except Exception as e:
                logger.error(f"Error running validation rule {rule.code}: {e}")
                all_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code=f"{rule.code}_EXECUTION_ERROR",
                    message=f"Validation rule failed to execute: {str(e)}",
                    field="validation_engine"
                ))

        return ValidationResult(
            is_valid=len([i for i in all_issues if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]) == 0,
            issues=all_issues
        )

    def add_rule(self, rule: ValidationRule):
        """Add a custom validation rule."""
        self.rules.append(rule)

    def remove_rule(self, code: str):
        """Remove a validation rule by code."""
        self.rules = [rule for rule in self.rules if rule.code != code]


class ValidationEngine:
    """Advanced validation engine with configurable rules and scoring."""

    def __init__(self):
        self.validator = RestaurantFinancialValidator()

    def validate_with_quality_score(self, income_statement: IncomeStatement) -> Tuple[ValidationResult, DataQualityScore]:
        """
        Validate data and calculate quality score.

        Args:
            income_statement: Financial data to validate

        Returns:
            Tuple of (ValidationResult, DataQualityScore)
        """
        validation_result = self.validator.validate(income_statement)
        quality_score = self._calculate_quality_score(income_statement, validation_result)

        return validation_result, quality_score

    def _calculate_quality_score(self, income_statement: IncomeStatement, validation_result: ValidationResult) -> DataQualityScore:
        """Calculate comprehensive data quality score."""

        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(income_statement)

        # Calculate accuracy score based on validation issues
        accuracy_score = self._calculate_accuracy_score(validation_result)

        # Calculate consistency score
        consistency_score = self._calculate_consistency_score(income_statement)

        # Category-specific quality scores
        revenue_quality = self._calculate_revenue_quality(income_statement.revenue)
        cost_quality = self._calculate_cost_quality(income_statement.costs)
        expense_quality = self._calculate_expense_quality(income_statement.expenses)

        # Overall score (weighted average)
        overall_score = (completeness_score * 0.3 + accuracy_score * 0.4 + consistency_score * 0.3)

        # Collect quality indicators
        missing_fields = self._identify_missing_fields(income_statement)
        suspicious_values = self._identify_suspicious_values(income_statement)
        calculation_errors = [issue.message for issue in validation_result.issues
                            if "calculation" in issue.message.lower()]

        return DataQualityScore(
            overall_score=overall_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            revenue_quality=revenue_quality,
            cost_quality=cost_quality,
            expense_quality=expense_quality,
            missing_fields=missing_fields,
            suspicious_values=suspicious_values,
            calculation_errors=calculation_errors
        )

    def _calculate_completeness_score(self, income_statement: IncomeStatement) -> float:
        """Calculate data completeness score."""
        total_fields = 20  # Total expected key fields
        filled_fields = 0

        # Check revenue fields
        if income_statement.revenue.total_revenue > 0:
            filled_fields += 1
        if income_statement.revenue.food_revenue > 0:
            filled_fields += 1
        if income_statement.revenue.beverage_revenue >= 0:
            filled_fields += 1

        # Check cost fields
        if income_statement.costs.total_cogs >= 0:
            filled_fields += 1
        if income_statement.costs.food_cost >= 0:
            filled_fields += 1

        # Check expense fields
        if income_statement.expenses.total_operating_expenses >= 0:
            filled_fields += 1
        if income_statement.expenses.labor_cost >= 0:
            filled_fields += 1
        if income_statement.expenses.rent_expense >= 0:
            filled_fields += 1

        # Check calculated metrics
        if income_statement.metrics.gross_profit is not None:
            filled_fields += 1
        if income_statement.metrics.gross_margin is not None:
            filled_fields += 1

        return min(filled_fields / total_fields, 1.0)

    def _calculate_accuracy_score(self, validation_result: ValidationResult) -> float:
        """Calculate accuracy score based on validation issues."""
        if not validation_result.issues:
            return 1.0

        # Weight different severity levels
        severity_weights = {
            ValidationSeverity.INFO: 0.0,
            ValidationSeverity.WARNING: 0.1,
            ValidationSeverity.ERROR: 0.3,
            ValidationSeverity.CRITICAL: 0.5
        }

        total_penalty = sum(severity_weights.get(issue.severity, 0.2) for issue in validation_result.issues)
        max_possible_penalty = len(validation_result.issues) * 0.5

        if max_possible_penalty == 0:
            return 1.0

        return max(0.0, 1.0 - (total_penalty / max_possible_penalty))

    def _calculate_consistency_score(self, income_statement: IncomeStatement) -> float:
        """Calculate data consistency score."""
        consistency_checks = 0
        passed_checks = 0

        # Revenue component consistency
        consistency_checks += 1
        revenue = income_statement.revenue
        component_sum = (revenue.food_revenue + revenue.beverage_revenue +
                        revenue.dessert_revenue + revenue.other_revenue + revenue.discounts)
        tolerance = abs(revenue.total_revenue * Decimal('0.02'))
        if abs(revenue.total_revenue - component_sum) <= tolerance:
            passed_checks += 1

        # Gross profit consistency
        consistency_checks += 1
        calculated_gross = revenue.total_revenue - income_statement.costs.total_cogs
        if abs(calculated_gross - income_statement.metrics.gross_profit) <= tolerance:
            passed_checks += 1

        # Margin consistency
        consistency_checks += 1
        if revenue.total_revenue > 0:
            calculated_margin = income_statement.metrics.gross_profit / revenue.total_revenue
            margin_tolerance = Decimal('0.01')
            if abs(calculated_margin - income_statement.metrics.gross_margin) <= margin_tolerance:
                passed_checks += 1

        return passed_checks / consistency_checks if consistency_checks > 0 else 1.0

    def _calculate_revenue_quality(self, revenue: RevenueBreakdown) -> float:
        """Calculate revenue data quality."""
        score = 1.0

        # Penalize for missing revenue breakdown
        if revenue.food_revenue == 0 and revenue.total_revenue > 0:
            score -= 0.2

        # Penalize for unrealistic revenue mix
        if revenue.total_revenue > 0:
            food_ratio = revenue.food_revenue / revenue.total_revenue
            if food_ratio < Decimal('0.5') or food_ratio > Decimal('0.95'):
                score -= 0.1

        return max(0.0, score)

    def _calculate_cost_quality(self, costs: CostBreakdown) -> float:
        """Calculate cost data quality."""
        score = 1.0

        # Penalize for missing cost breakdown
        if costs.food_cost == 0 and costs.total_cogs > 0:
            score -= 0.2

        return max(0.0, score)

    def _calculate_expense_quality(self, expenses: ExpenseBreakdown) -> float:
        """Calculate expense data quality."""
        score = 1.0

        # Penalize for missing labor cost
        if expenses.labor_cost == 0 and expenses.total_operating_expenses > 0:
            score -= 0.2

        return max(0.0, score)

    def _identify_missing_fields(self, income_statement: IncomeStatement) -> List[str]:
        """Identify missing critical fields."""
        missing = []

        if income_statement.revenue.food_revenue == 0:
            missing.append("food_revenue")
        if income_statement.costs.food_cost == 0:
            missing.append("food_cost")
        if income_statement.expenses.labor_cost == 0:
            missing.append("labor_cost")

        return missing

    def _identify_suspicious_values(self, income_statement: IncomeStatement) -> List[str]:
        """Identify suspicious values that warrant review."""
        suspicious = []

        # Unusually high margins
        if income_statement.metrics.gross_margin > Decimal('0.9'):
            suspicious.append(f"Very high gross margin: {income_statement.metrics.gross_margin:.1%}")

        # Unusually low costs
        if income_statement.revenue.total_revenue > 0:
            cost_ratio = income_statement.costs.total_cogs / income_statement.revenue.total_revenue
            if cost_ratio < Decimal('0.1'):
                suspicious.append(f"Very low cost ratio: {cost_ratio:.1%}")

        return suspicious