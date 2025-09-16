"""
Comparative Analysis Engine for Restaurant Financial Data

This module provides comparative analysis capabilities including
peer comparisons, benchmarking, and performance ranking.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import statistics
import logging

from ..models.financial_data import IncomeStatement
from .kpi_calculator import KPICalculator, RestaurantKPIs, KPIMetric

logger = logging.getLogger(__name__)


class ComparisonType(str, Enum):
    """Types of comparisons."""
    PEER_TO_PEER = "peer_to_peer"
    BENCHMARK = "benchmark"
    HISTORICAL = "historical"
    INDUSTRY = "industry"


class PerformanceRating(str, Enum):
    """Performance ratings."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"


@dataclass
class ComparisonMetric:
    """Individual comparison metric."""
    name: str
    target_value: Decimal
    comparison_values: List[Decimal]
    target_rank: int  # 1-based ranking (1 = best)
    percentile: Decimal  # 0-100 percentile
    performance_rating: PerformanceRating
    variance_from_median: Decimal
    best_in_class: bool
    improvement_potential: Decimal  # How much improvement possible to reach top quartile


@dataclass
class ComparisonResult:
    """Complete comparison analysis result."""
    target_restaurant: str
    comparison_restaurants: List[str]
    comparison_type: ComparisonType
    metrics: Dict[str, ComparisonMetric]
    overall_score: Decimal  # 0-100 composite score
    rank_summary: Dict[str, int]  # Category rankings
    strengths: List[str]
    weaknesses: List[str]
    improvement_opportunities: List[Dict[str, Any]]

    def get_top_metrics(self, count: int = 5) -> List[ComparisonMetric]:
        """Get top performing metrics."""
        sorted_metrics = sorted(
            self.metrics.values(),
            key=lambda m: m.percentile,
            reverse=True
        )
        return sorted_metrics[:count]

    def get_bottom_metrics(self, count: int = 5) -> List[ComparisonMetric]:
        """Get bottom performing metrics."""
        sorted_metrics = sorted(
            self.metrics.values(),
            key=lambda m: m.percentile
        )
        return sorted_metrics[:count]


class ComparativeAnalyzer:
    """Engine for comparative financial analysis."""

    def __init__(self):
        self.kpi_calculator = KPICalculator()

    def compare_restaurants(
        self,
        target_statement: IncomeStatement,
        comparison_statements: List[IncomeStatement],
        comparison_type: ComparisonType = ComparisonType.PEER_TO_PEER
    ) -> ComparisonResult:
        """
        Compare a target restaurant against a group of comparison restaurants.

        Args:
            target_statement: Financial statement of the restaurant to analyze
            comparison_statements: List of comparison restaurant statements
            comparison_type: Type of comparison to perform

        Returns:
            Comprehensive comparison result
        """
        # Calculate KPIs for all restaurants
        target_kpis = self.kpi_calculator.calculate_all_kpis(target_statement)
        comparison_kpis = [
            self.kpi_calculator.calculate_all_kpis(stmt)
            for stmt in comparison_statements
        ]

        # Get all metric names
        all_metrics = target_kpis.get_all_metrics()

        # Perform comparisons
        comparison_metrics = {}
        for metric_name, target_metric in all_metrics.items():
            comparison_values = []
            for comp_kpis in comparison_kpis:
                comp_metrics = comp_kpis.get_all_metrics()
                if metric_name in comp_metrics:
                    comparison_values.append(comp_metrics[metric_name].value)

            if comparison_values:  # Only analyze if we have comparison data
                comparison_metrics[metric_name] = self._analyze_metric_comparison(
                    metric_name,
                    target_metric,
                    comparison_values
                )

        # Calculate overall performance
        overall_score = self._calculate_overall_score(comparison_metrics)

        # Generate rankings by category
        rank_summary = self._calculate_category_rankings(target_kpis, comparison_kpis)

        # Identify strengths and weaknesses
        strengths = self._identify_strengths(comparison_metrics)
        weaknesses = self._identify_weaknesses(comparison_metrics)

        # Generate improvement opportunities
        opportunities = self._generate_improvement_opportunities(comparison_metrics, target_kpis)

        # Create restaurant names
        target_name = target_statement.restaurant_name or "Target Restaurant"
        comparison_names = [
            stmt.restaurant_name or f"Restaurant {i+1}"
            for i, stmt in enumerate(comparison_statements)
        ]

        return ComparisonResult(
            target_restaurant=target_name,
            comparison_restaurants=comparison_names,
            comparison_type=comparison_type,
            metrics=comparison_metrics,
            overall_score=overall_score,
            rank_summary=rank_summary,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_opportunities=opportunities
        )

    def _analyze_metric_comparison(
        self,
        metric_name: str,
        target_metric: KPIMetric,
        comparison_values: List[Decimal]
    ) -> ComparisonMetric:
        """Analyze comparison for a single metric."""
        target_value = target_metric.value
        all_values = comparison_values + [target_value]

        # Calculate ranking
        sorted_values = sorted(all_values, reverse=target_metric.is_higher_better)
        target_rank = sorted_values.index(target_value) + 1

        # Calculate percentile
        values_below = len([v for v in comparison_values if
                          (v < target_value if target_metric.is_higher_better else v > target_value)])
        percentile = Decimal(str(values_below)) / Decimal(str(len(comparison_values))) * 100

        # Determine performance rating
        performance_rating = self._determine_performance_rating(percentile)

        # Calculate variance from median
        median_value = Decimal(str(statistics.median([float(v) for v in comparison_values])))
        variance_from_median = target_value - median_value

        # Check if best in class
        best_in_class = target_rank == 1

        # Calculate improvement potential (to reach 75th percentile)
        top_quartile_threshold = self._calculate_percentile_value(comparison_values, 75, target_metric.is_higher_better)
        if target_metric.is_higher_better:
            improvement_potential = max(Decimal("0"), top_quartile_threshold - target_value)
        else:
            improvement_potential = max(Decimal("0"), target_value - top_quartile_threshold)

        return ComparisonMetric(
            name=metric_name,
            target_value=target_value,
            comparison_values=comparison_values,
            target_rank=target_rank,
            percentile=percentile,
            performance_rating=performance_rating,
            variance_from_median=variance_from_median,
            best_in_class=best_in_class,
            improvement_potential=improvement_potential
        )

    def _determine_performance_rating(self, percentile: Decimal) -> PerformanceRating:
        """Determine performance rating based on percentile."""
        if percentile >= 90:
            return PerformanceRating.EXCELLENT
        elif percentile >= 75:
            return PerformanceRating.GOOD
        elif percentile >= 50:
            return PerformanceRating.AVERAGE
        elif percentile >= 25:
            return PerformanceRating.BELOW_AVERAGE
        else:
            return PerformanceRating.POOR

    def _calculate_percentile_value(
        self,
        values: List[Decimal],
        percentile: int,
        higher_better: bool
    ) -> Decimal:
        """Calculate the value at a given percentile."""
        float_values = [float(v) for v in values]

        # Sort based on whether higher is better
        sorted_values = sorted(float_values, reverse=higher_better)

        # Calculate percentile index
        index = (percentile / 100) * (len(sorted_values) - 1)

        # Interpolate if needed
        if index == int(index):
            return Decimal(str(sorted_values[int(index)]))
        else:
            lower_idx = int(index)
            upper_idx = min(lower_idx + 1, len(sorted_values) - 1)
            weight = index - lower_idx

            interpolated = (
                sorted_values[lower_idx] * (1 - weight) +
                sorted_values[upper_idx] * weight
            )
            return Decimal(str(interpolated))

    def _calculate_overall_score(self, metrics: Dict[str, ComparisonMetric]) -> Decimal:
        """Calculate overall composite score."""
        if not metrics:
            return Decimal("0")

        # Weight different metric categories
        weights = {
            "profitability": Decimal("0.35"),
            "efficiency": Decimal("0.25"),
            "cost_control": Decimal("0.25"),
            "operational": Decimal("0.15")
        }

        category_scores = {}
        category_counts = {}

        for metric_name, metric in metrics.items():
            # Categorize metrics (simplified categorization)
            category = self._categorize_metric(metric_name)

            if category not in category_scores:
                category_scores[category] = Decimal("0")
                category_counts[category] = 0

            category_scores[category] += metric.percentile
            category_counts[category] += 1

        # Calculate weighted average
        total_score = Decimal("0")
        total_weight = Decimal("0")

        for category, total_percentile in category_scores.items():
            if category_counts[category] > 0:
                avg_percentile = total_percentile / category_counts[category]
                weight = weights.get(category, Decimal("0.1"))
                total_score += avg_percentile * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else Decimal("0")

    def _categorize_metric(self, metric_name: str) -> str:
        """Categorize a metric for weighting purposes."""
        profit_metrics = ["gross_profit_margin", "operating_profit_margin", "revenue_per_cost_dollar"]
        efficiency_metrics = ["revenue_per_labor_dollar", "expense_turnover", "food_cost_efficiency"]
        cost_metrics = ["food_cost_percentage", "labor_cost_percentage", "prime_cost_percentage"]

        if metric_name in profit_metrics:
            return "profitability"
        elif metric_name in efficiency_metrics:
            return "efficiency"
        elif metric_name in cost_metrics:
            return "cost_control"
        else:
            return "operational"

    def _calculate_category_rankings(
        self,
        target_kpis: RestaurantKPIs,
        comparison_kpis: List[RestaurantKPIs]
    ) -> Dict[str, int]:
        """Calculate rankings by KPI category."""
        rankings = {}

        # Get category averages for target
        target_categories = {
            "profitability": self._average_category_percentile(target_kpis.profitability),
            "efficiency": self._average_category_percentile(target_kpis.efficiency),
            "cost_control": self._average_category_percentile(target_kpis.cost_control),
            "revenue_mix": self._average_category_percentile(target_kpis.revenue_mix),
            "operational": self._average_category_percentile(target_kpis.operational)
        }

        # Compare against peer group (simplified ranking)
        for category, score in target_categories.items():
            # This is a simplified ranking - in practice, you'd compare
            # each category against the same categories in comparison restaurants
            rankings[category] = 1  # Placeholder ranking

        return rankings

    def _average_category_percentile(self, category_metrics: Dict[str, KPIMetric]) -> Decimal:
        """Calculate average percentile for a category (placeholder)."""
        if not category_metrics:
            return Decimal("50")  # Neutral percentile

        # This is simplified - in practice, you'd have actual percentile calculations
        return Decimal("50")

    def _identify_strengths(self, metrics: Dict[str, ComparisonMetric]) -> List[str]:
        """Identify top performing areas."""
        strengths = []

        # Find metrics in top quartile
        top_metrics = [
            metric for metric in metrics.values()
            if metric.percentile >= 75
        ]

        if not top_metrics:
            return ["No clear strengths identified in this peer group"]

        # Group by performance area
        strength_areas = {}
        for metric in top_metrics:
            category = self._categorize_metric(metric.name)
            if category not in strength_areas:
                strength_areas[category] = []
            strength_areas[category].append(metric)

        # Generate strength statements
        for category, category_metrics in strength_areas.items():
            if len(category_metrics) >= 2:
                strengths.append(f"Strong {category} performance with multiple metrics in top quartile")
            else:
                metric = category_metrics[0]
                strengths.append(f"Excellent {metric.name.replace('_', ' ')} performance (rank #{metric.target_rank})")

        return strengths[:5]  # Limit to top 5 strengths

    def _identify_weaknesses(self, metrics: Dict[str, ComparisonMetric]) -> List[str]:
        """Identify bottom performing areas."""
        weaknesses = []

        # Find metrics in bottom quartile
        bottom_metrics = [
            metric for metric in metrics.values()
            if metric.percentile <= 25
        ]

        if not bottom_metrics:
            return ["No significant weaknesses identified in this peer group"]

        # Sort by percentile (worst first)
        bottom_metrics.sort(key=lambda m: m.percentile)

        # Generate weakness statements
        for metric in bottom_metrics[:3]:  # Top 3 weaknesses
            weakness_text = f"Below-average {metric.name.replace('_', ' ')} (bottom {100-metric.percentile:.0f}%)"
            if metric.improvement_potential > 0:
                if "percentage" in metric.name or "ratio" in metric.name:
                    improvement = f"{metric.improvement_potential:.1%}"
                else:
                    improvement = f"{metric.improvement_potential:.0f}"
                weakness_text += f" - potential improvement: {improvement}"
            weaknesses.append(weakness_text)

        return weaknesses

    def _generate_improvement_opportunities(
        self,
        metrics: Dict[str, ComparisonMetric],
        target_kpis: RestaurantKPIs
    ) -> List[Dict[str, Any]]:
        """Generate specific improvement opportunities."""
        opportunities = []

        # Find metrics with significant improvement potential
        improvement_metrics = [
            metric for metric in metrics.values()
            if metric.improvement_potential > 0 and metric.percentile < 75
        ]

        # Sort by improvement potential
        improvement_metrics.sort(key=lambda m: m.improvement_potential, reverse=True)

        for metric in improvement_metrics[:5]:  # Top 5 opportunities
            opportunity = {
                "metric": metric.name,
                "current_value": metric.target_value,
                "target_value": metric.target_value + metric.improvement_potential,
                "improvement_potential": metric.improvement_potential,
                "current_rank": metric.target_rank,
                "actions": self._suggest_improvement_actions(metric.name, metric.improvement_potential)
            }
            opportunities.append(opportunity)

        return opportunities

    def _suggest_improvement_actions(self, metric_name: str, improvement_potential: Decimal) -> List[str]:
        """Suggest specific actions for improvement."""
        actions = []

        if "food_cost" in metric_name:
            actions = [
                "Review supplier contracts and negotiate better rates",
                "Implement portion control and waste reduction programs",
                "Optimize menu mix toward higher-margin items",
                "Improve inventory management and reduce spoilage"
            ]
        elif "labor_cost" in metric_name:
            actions = [
                "Optimize staff scheduling and reduce overtime",
                "Implement cross-training to improve flexibility",
                "Review productivity metrics and provide training",
                "Consider automation opportunities"
            ]
        elif "revenue" in metric_name:
            actions = [
                "Enhance marketing and customer acquisition",
                "Optimize menu pricing and upselling strategies",
                "Improve customer experience and retention",
                "Expand operating hours or service offerings"
            ]
        elif "margin" in metric_name:
            actions = [
                "Review and optimize menu pricing",
                "Focus on cost reduction initiatives",
                "Improve operational efficiency",
                "Enhance revenue per customer"
            ]
        else:
            actions = [
                "Conduct detailed operational review",
                "Benchmark against top performers",
                "Implement best practices from industry leaders"
            ]

        return actions

    def compare_to_benchmarks(
        self,
        target_statement: IncomeStatement,
        benchmarks: Dict[str, Decimal]
    ) -> ComparisonResult:
        """Compare restaurant performance to industry benchmarks."""
        target_kpis = self.kpi_calculator.calculate_all_kpis(target_statement)
        target_metrics = target_kpis.get_all_metrics()

        comparison_metrics = {}

        for metric_name, target_metric in target_metrics.items():
            if metric_name in benchmarks:
                benchmark_value = benchmarks[metric_name]

                # Create comparison with benchmark as the comparison point
                comparison_metrics[metric_name] = self._compare_to_single_benchmark(
                    metric_name,
                    target_metric,
                    benchmark_value
                )

        # Calculate overall score against benchmarks
        overall_score = self._calculate_benchmark_score(comparison_metrics)

        return ComparisonResult(
            target_restaurant=target_statement.restaurant_name or "Target Restaurant",
            comparison_restaurants=["Industry Benchmark"],
            comparison_type=ComparisonType.BENCHMARK,
            metrics=comparison_metrics,
            overall_score=overall_score,
            rank_summary={},
            strengths=self._identify_benchmark_strengths(comparison_metrics),
            weaknesses=self._identify_benchmark_weaknesses(comparison_metrics),
            improvement_opportunities=[]
        )

    def _compare_to_single_benchmark(
        self,
        metric_name: str,
        target_metric: KPIMetric,
        benchmark_value: Decimal
    ) -> ComparisonMetric:
        """Compare a single metric to its benchmark."""
        target_value = target_metric.value

        # Calculate performance relative to benchmark
        if target_metric.is_higher_better:
            performance_ratio = target_value / benchmark_value if benchmark_value != 0 else Decimal("1")
            percentile = min(performance_ratio * 50, 100)  # Scale to percentile
        else:
            performance_ratio = benchmark_value / target_value if target_value != 0 else Decimal("1")
            percentile = min(performance_ratio * 50, 100)

        # Determine rating
        rating = self._determine_performance_rating(percentile)

        return ComparisonMetric(
            name=metric_name,
            target_value=target_value,
            comparison_values=[benchmark_value],
            target_rank=1 if percentile > 50 else 2,
            percentile=percentile,
            performance_rating=rating,
            variance_from_median=target_value - benchmark_value,
            best_in_class=percentile > 50,
            improvement_potential=max(Decimal("0"), abs(target_value - benchmark_value))
        )

    def _calculate_benchmark_score(self, metrics: Dict[str, ComparisonMetric]) -> Decimal:
        """Calculate overall score against benchmarks."""
        if not metrics:
            return Decimal("50")

        total_score = sum(metric.percentile for metric in metrics.values())
        return total_score / len(metrics)

    def _identify_benchmark_strengths(self, metrics: Dict[str, ComparisonMetric]) -> List[str]:
        """Identify strengths against benchmarks."""
        above_benchmark = [m for m in metrics.values() if m.percentile > 50]

        strengths = []
        for metric in above_benchmark:
            improvement_text = f"{metric.name.replace('_', ' ')} exceeds industry benchmark"
            strengths.append(improvement_text)

        return strengths[:5]

    def _identify_benchmark_weaknesses(self, metrics: Dict[str, ComparisonMetric]) -> List[str]:
        """Identify weaknesses against benchmarks."""
        below_benchmark = [m for m in metrics.values() if m.percentile <= 50]

        weaknesses = []
        for metric in below_benchmark:
            weakness_text = f"{metric.name.replace('_', ' ')} below industry benchmark"
            weaknesses.append(weakness_text)

        return weaknesses[:5]