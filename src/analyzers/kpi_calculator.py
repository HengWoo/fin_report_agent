"""
KPI Calculator for Restaurant Financial Analysis

This module calculates key performance indicators specific to restaurant operations,
including profitability, efficiency, and operational metrics.
"""

from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import logging

from ..models.financial_data import IncomeStatement, ProfitMetrics

logger = logging.getLogger(__name__)


class KPICategory(str, Enum):
    """Categories of restaurant KPIs."""
    PROFITABILITY = "profitability"
    EFFICIENCY = "efficiency"
    COST_CONTROL = "cost_control"
    REVENUE_MIX = "revenue_mix"
    OPERATIONAL = "operational"


@dataclass
class KPIMetric:
    """Individual KPI metric with metadata."""
    name: str
    value: Decimal
    category: KPICategory
    unit: str  # "percentage", "currency", "ratio", "days"
    description: str
    benchmark_min: Optional[Decimal] = None
    benchmark_max: Optional[Decimal] = None
    is_higher_better: bool = True

    @property
    def performance_status(self) -> str:
        """Determine performance status against benchmarks."""
        if self.benchmark_min is None or self.benchmark_max is None:
            return "unknown"

        if self.is_higher_better:
            if self.value >= self.benchmark_max:
                return "excellent"
            elif self.value >= self.benchmark_min:
                return "good"
            else:
                return "poor"
        else:
            if self.value <= self.benchmark_min:
                return "excellent"
            elif self.value <= self.benchmark_max:
                return "good"
            else:
                return "poor"

    def format_value(self) -> str:
        """Format the value for display."""
        if self.unit == "percentage":
            return f"{self.value:.1%}"
        elif self.unit == "currency":
            return f"¥{self.value:,.0f}"
        elif self.unit == "ratio":
            return f"{self.value:.2f}"
        elif self.unit == "days":
            return f"{self.value:.0f} days"
        else:
            return str(self.value)


@dataclass
class RestaurantKPIs:
    """Complete set of restaurant KPIs organized by category."""
    profitability: Dict[str, KPIMetric]
    efficiency: Dict[str, KPIMetric]
    cost_control: Dict[str, KPIMetric]
    revenue_mix: Dict[str, KPIMetric]
    operational: Dict[str, KPIMetric]

    def get_all_metrics(self) -> Dict[str, KPIMetric]:
        """Get all metrics in a flat dictionary."""
        all_metrics = {}
        all_metrics.update(self.profitability)
        all_metrics.update(self.efficiency)
        all_metrics.update(self.cost_control)
        all_metrics.update(self.revenue_mix)
        all_metrics.update(self.operational)
        return all_metrics

    def get_by_category(self, category: KPICategory) -> Dict[str, KPIMetric]:
        """Get metrics by category."""
        if category == KPICategory.PROFITABILITY:
            return self.profitability
        elif category == KPICategory.EFFICIENCY:
            return self.efficiency
        elif category == KPICategory.COST_CONTROL:
            return self.cost_control
        elif category == KPICategory.REVENUE_MIX:
            return self.revenue_mix
        elif category == KPICategory.OPERATIONAL:
            return self.operational
        else:
            return {}

    def get_performance_summary(self) -> Dict[str, int]:
        """Get summary of performance across all KPIs."""
        all_metrics = self.get_all_metrics()
        summary = {"excellent": 0, "good": 0, "poor": 0, "unknown": 0}

        for metric in all_metrics.values():
            status = metric.performance_status
            summary[status] += 1

        return summary


class KPICalculator:
    """Calculator for restaurant-specific KPIs."""

    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()

    def calculate_all_kpis(self, income_statement: IncomeStatement) -> RestaurantKPIs:
        """
        Calculate all restaurant KPIs from an income statement.

        Args:
            income_statement: Validated income statement data

        Returns:
            Complete set of calculated KPIs
        """
        revenue = income_statement.revenue
        costs = income_statement.costs
        expenses = income_statement.expenses
        metrics = income_statement.metrics

        # Calculate profitability KPIs
        profitability = self._calculate_profitability_kpis(revenue, costs, expenses, metrics)

        # Calculate efficiency KPIs
        efficiency = self._calculate_efficiency_kpis(revenue, costs, expenses, metrics)

        # Calculate cost control KPIs
        cost_control = self._calculate_cost_control_kpis(revenue, costs, expenses, metrics)

        # Calculate revenue mix KPIs
        revenue_mix = self._calculate_revenue_mix_kpis(revenue, metrics)

        # Calculate operational KPIs
        operational = self._calculate_operational_kpis(revenue, costs, expenses, metrics)

        return RestaurantKPIs(
            profitability=profitability,
            efficiency=efficiency,
            cost_control=cost_control,
            revenue_mix=revenue_mix,
            operational=operational
        )

    def _calculate_profitability_kpis(self, revenue, costs, expenses, metrics) -> Dict[str, KPIMetric]:
        """Calculate profitability-related KPIs."""
        kpis = {}

        # Gross Profit Margin
        kpis["gross_profit_margin"] = KPIMetric(
            name="Gross Profit Margin",
            value=metrics.gross_margin,
            category=KPICategory.PROFITABILITY,
            unit="percentage",
            description="Revenue minus cost of goods sold as percentage of revenue",
            benchmark_min=Decimal("0.55"),
            benchmark_max=Decimal("0.75"),
            is_higher_better=True
        )

        # Operating Profit Margin
        kpis["operating_profit_margin"] = KPIMetric(
            name="Operating Profit Margin",
            value=metrics.operating_margin,
            category=KPICategory.PROFITABILITY,
            unit="percentage",
            description="Operating profit as percentage of revenue",
            benchmark_min=Decimal("0.10"),
            benchmark_max=Decimal("0.20"),
            is_higher_better=True
        )

        # Revenue Per Dollar of Costs (Revenue Efficiency)
        if costs.total_cogs > 0:
            revenue_per_cost = revenue.total_revenue / costs.total_cogs
            kpis["revenue_per_cost_dollar"] = KPIMetric(
                name="Revenue per Cost Dollar",
                value=revenue_per_cost,
                category=KPICategory.PROFITABILITY,
                unit="ratio",
                description="Revenue generated per dollar of cost",
                benchmark_min=Decimal("2.5"),
                benchmark_max=Decimal("4.0"),
                is_higher_better=True
            )

        # EBITDA Margin (approximated as operating margin + estimated depreciation)
        # For restaurants, assume ~3-5% depreciation
        estimated_ebitda_margin = metrics.operating_margin + Decimal("0.04")
        kpis["estimated_ebitda_margin"] = KPIMetric(
            name="Estimated EBITDA Margin",
            value=estimated_ebitda_margin,
            category=KPICategory.PROFITABILITY,
            unit="percentage",
            description="Estimated earnings before interest, taxes, depreciation, and amortization",
            benchmark_min=Decimal("0.15"),
            benchmark_max=Decimal("0.25"),
            is_higher_better=True
        )

        return kpis

    def _calculate_efficiency_kpis(self, revenue, costs, expenses, metrics) -> Dict[str, KPIMetric]:
        """Calculate operational efficiency KPIs."""
        kpis = {}

        # Revenue per Labor Dollar
        if expenses.labor_cost > 0:
            revenue_per_labor = revenue.total_revenue / expenses.labor_cost
            kpis["revenue_per_labor_dollar"] = KPIMetric(
                name="Revenue per Labor Dollar",
                value=revenue_per_labor,
                category=KPICategory.EFFICIENCY,
                unit="ratio",
                description="Revenue generated per dollar of labor cost",
                benchmark_min=Decimal("3.0"),
                benchmark_max=Decimal("5.0"),
                is_higher_better=True
            )

        # Asset Turnover (approximated using revenue/total expenses as proxy)
        total_expenses = costs.total_cogs + expenses.total_operating_expenses
        if total_expenses > 0:
            expense_turnover = revenue.total_revenue / total_expenses
            kpis["expense_turnover"] = KPIMetric(
                name="Expense Turnover",
                value=expense_turnover,
                category=KPICategory.EFFICIENCY,
                unit="ratio",
                description="Revenue generated per dollar of total expenses",
                benchmark_min=Decimal("1.2"),
                benchmark_max=Decimal("1.8"),
                is_higher_better=True
            )

        # Food Cost Efficiency (Revenue per Food Cost Dollar)
        if costs.food_cost > 0:
            food_cost_efficiency = revenue.food_revenue / costs.food_cost if revenue.food_revenue > 0 else revenue.total_revenue / costs.food_cost
            kpis["food_cost_efficiency"] = KPIMetric(
                name="Food Cost Efficiency",
                value=food_cost_efficiency,
                category=KPICategory.EFFICIENCY,
                unit="ratio",
                description="Food revenue generated per dollar of food cost",
                benchmark_min=Decimal("2.5"),
                benchmark_max=Decimal("4.0"),
                is_higher_better=True
            )

        return kpis

    def _calculate_cost_control_kpis(self, revenue, costs, expenses, metrics) -> Dict[str, KPIMetric]:
        """Calculate cost control KPIs."""
        kpis = {}

        # Food Cost Percentage
        if metrics.food_cost_ratio is not None:
            kpis["food_cost_percentage"] = KPIMetric(
                name="Food Cost Percentage",
                value=metrics.food_cost_ratio,
                category=KPICategory.COST_CONTROL,
                unit="percentage",
                description="Food costs as percentage of food revenue",
                benchmark_min=Decimal("0.25"),
                benchmark_max=Decimal("0.35"),
                is_higher_better=False
            )

        # Labor Cost Percentage
        if metrics.labor_cost_ratio is not None:
            kpis["labor_cost_percentage"] = KPIMetric(
                name="Labor Cost Percentage",
                value=metrics.labor_cost_ratio,
                category=KPICategory.COST_CONTROL,
                unit="percentage",
                description="Labor costs as percentage of total revenue",
                benchmark_min=Decimal("0.20"),
                benchmark_max=Decimal("0.30"),
                is_higher_better=False
            )

        # Prime Cost Percentage
        if metrics.prime_cost_ratio is not None:
            kpis["prime_cost_percentage"] = KPIMetric(
                name="Prime Cost Percentage",
                value=metrics.prime_cost_ratio,
                category=KPICategory.COST_CONTROL,
                unit="percentage",
                description="Combined food and labor costs as percentage of revenue",
                benchmark_min=Decimal("0.50"),
                benchmark_max=Decimal("0.65"),
                is_higher_better=False
            )

        # Rent-to-Revenue Ratio
        if expenses.rent_expense > 0 and revenue.total_revenue > 0:
            rent_ratio = expenses.rent_expense / revenue.total_revenue
            kpis["rent_to_revenue_ratio"] = KPIMetric(
                name="Rent to Revenue Ratio",
                value=rent_ratio,
                category=KPICategory.COST_CONTROL,
                unit="percentage",
                description="Rent expense as percentage of revenue",
                benchmark_min=Decimal("0.06"),
                benchmark_max=Decimal("0.12"),
                is_higher_better=False
            )

        # Variable Cost Percentage (approximated as COGS/Revenue)
        variable_cost_ratio = costs.total_cogs / revenue.total_revenue if revenue.total_revenue > 0 else Decimal("0")
        kpis["variable_cost_percentage"] = KPIMetric(
            name="Variable Cost Percentage",
            value=variable_cost_ratio,
            category=KPICategory.COST_CONTROL,
            unit="percentage",
            description="Variable costs (COGS) as percentage of revenue",
            benchmark_min=Decimal("0.25"),
            benchmark_max=Decimal("0.45"),
            is_higher_better=False
        )

        return kpis

    def _calculate_revenue_mix_kpis(self, revenue, metrics) -> Dict[str, KPIMetric]:
        """Calculate revenue mix and composition KPIs."""
        kpis = {}

        if revenue.total_revenue > 0:
            # Food Revenue Mix
            food_revenue_mix = revenue.food_revenue / revenue.total_revenue
            kpis["food_revenue_mix"] = KPIMetric(
                name="Food Revenue Mix",
                value=food_revenue_mix,
                category=KPICategory.REVENUE_MIX,
                unit="percentage",
                description="Food revenue as percentage of total revenue",
                benchmark_min=Decimal("0.70"),
                benchmark_max=Decimal("0.85"),
                is_higher_better=None  # Not necessarily better or worse
            )

            # Beverage Revenue Mix
            beverage_revenue_mix = revenue.beverage_revenue / revenue.total_revenue
            kpis["beverage_revenue_mix"] = KPIMetric(
                name="Beverage Revenue Mix",
                value=beverage_revenue_mix,
                category=KPICategory.REVENUE_MIX,
                unit="percentage",
                description="Beverage revenue as percentage of total revenue",
                benchmark_min=Decimal("0.10"),
                benchmark_max=Decimal("0.25"),
                is_higher_better=None
            )

            # High-Margin Item Mix (Desserts + Beverages)
            high_margin_mix = (revenue.dessert_revenue + revenue.beverage_revenue) / revenue.total_revenue
            kpis["high_margin_item_mix"] = KPIMetric(
                name="High-Margin Item Mix",
                value=high_margin_mix,
                category=KPICategory.REVENUE_MIX,
                unit="percentage",
                description="High-margin items (desserts + beverages) as percentage of revenue",
                benchmark_min=Decimal("0.15"),
                benchmark_max=Decimal("0.30"),
                is_higher_better=True
            )

            # Discount Rate (if discounts are negative)
            if revenue.discounts < 0:
                discount_rate = abs(revenue.discounts) / revenue.total_revenue
                kpis["discount_rate"] = KPIMetric(
                    name="Discount Rate",
                    value=discount_rate,
                    category=KPICategory.REVENUE_MIX,
                    unit="percentage",
                    description="Discounts as percentage of total revenue",
                    benchmark_min=Decimal("0.02"),
                    benchmark_max=Decimal("0.08"),
                    is_higher_better=False
                )

        return kpis

    def _calculate_operational_kpis(self, revenue, costs, expenses, metrics) -> Dict[str, KPIMetric]:
        """Calculate operational efficiency KPIs."""
        kpis = {}

        # Break-even Revenue (Fixed costs / Gross margin)
        if metrics.gross_margin > 0:
            # Estimate fixed costs as rent + portion of labor + utilities
            estimated_fixed_costs = expenses.rent_expense + (expenses.labor_cost * Decimal("0.6")) + expenses.utilities
            breakeven_revenue = estimated_fixed_costs / metrics.gross_margin

            kpis["breakeven_revenue"] = KPIMetric(
                name="Break-even Revenue",
                value=breakeven_revenue,
                category=KPICategory.OPERATIONAL,
                unit="currency",
                description="Monthly revenue needed to break even",
                is_higher_better=False
            )

            # Revenue Above Break-even
            revenue_above_breakeven = revenue.total_revenue - breakeven_revenue
            kpis["revenue_above_breakeven"] = KPIMetric(
                name="Revenue Above Break-even",
                value=revenue_above_breakeven,
                category=KPICategory.OPERATIONAL,
                unit="currency",
                description="Revenue above break-even point",
                is_higher_better=True
            )

        # Cash Conversion Efficiency (Operating Profit / Revenue)
        # This approximates how efficiently the restaurant converts sales to cash
        cash_conversion = metrics.operating_profit / revenue.total_revenue if revenue.total_revenue > 0 else Decimal("0")
        kpis["cash_conversion_efficiency"] = KPIMetric(
            name="Cash Conversion Efficiency",
            value=cash_conversion,
            category=KPICategory.OPERATIONAL,
            unit="percentage",
            description="Operating profit as percentage of revenue (cash generation efficiency)",
            benchmark_min=Decimal("0.08"),
            benchmark_max=Decimal("0.18"),
            is_higher_better=True
        )

        # Labor Productivity (Revenue per Labor Dollar)
        if expenses.labor_cost > 0:
            labor_productivity = revenue.total_revenue / expenses.labor_cost
            kpis["labor_productivity"] = KPIMetric(
                name="Labor Productivity",
                value=labor_productivity,
                category=KPICategory.OPERATIONAL,
                unit="ratio",
                description="Revenue generated per dollar of labor cost",
                benchmark_min=Decimal("3.0"),
                benchmark_max=Decimal("5.0"),
                is_higher_better=True
            )

        return kpis

    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, Decimal]]:
        """Load restaurant industry benchmarks."""
        return {
            "quick_service": {
                "gross_margin": {"min": Decimal("0.60"), "max": Decimal("0.75")},
                "labor_cost_ratio": {"min": Decimal("0.25"), "max": Decimal("0.35")},
                "food_cost_ratio": {"min": Decimal("0.28"), "max": Decimal("0.35")}
            },
            "casual_dining": {
                "gross_margin": {"min": Decimal("0.55"), "max": Decimal("0.70")},
                "labor_cost_ratio": {"min": Decimal("0.28"), "max": Decimal("0.35")},
                "food_cost_ratio": {"min": Decimal("0.30"), "max": Decimal("0.38")}
            },
            "fine_dining": {
                "gross_margin": {"min": Decimal("0.50"), "max": Decimal("0.65")},
                "labor_cost_ratio": {"min": Decimal("0.35"), "max": Decimal("0.45")},
                "food_cost_ratio": {"min": Decimal("0.32"), "max": Decimal("0.42")}
            }
        }

    def calculate_kpi_trends(self, historical_statements: List[IncomeStatement]) -> Dict[str, List[Decimal]]:
        """
        Calculate KPI trends over multiple periods.

        Args:
            historical_statements: List of income statements in chronological order

        Returns:
            Dictionary mapping KPI names to their historical values
        """
        trends = {}

        for statement in historical_statements:
            kpis = self.calculate_all_kpis(statement)
            all_metrics = kpis.get_all_metrics()

            for kpi_name, metric in all_metrics.items():
                if kpi_name not in trends:
                    trends[kpi_name] = []
                trends[kpi_name].append(metric.value)

        return trends

    def benchmark_against_industry(self, kpis: RestaurantKPIs, restaurant_type: str = "casual_dining") -> Dict[str, str]:
        """
        Benchmark KPIs against industry standards.

        Args:
            kpis: Calculated restaurant KPIs
            restaurant_type: Type of restaurant for benchmarking

        Returns:
            Dictionary mapping KPI names to performance assessments
        """
        benchmarks = self.industry_benchmarks.get(restaurant_type, {})
        assessments = {}

        all_metrics = kpis.get_all_metrics()

        for kpi_name, metric in all_metrics.items():
            if metric.benchmark_min is not None and metric.benchmark_max is not None:
                assessments[kpi_name] = metric.performance_status
            else:
                assessments[kpi_name] = "no_benchmark"

        return assessments