"""
Trend Analysis Engine for Restaurant Financial Data

This module provides sophisticated trend analysis capabilities including
growth calculations, seasonality detection, and forecasting.
"""

from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import statistics
import logging
from datetime import datetime, timedelta

from ..models.financial_data import IncomeStatement, FinancialPeriod

logger = logging.getLogger(__name__)


class TrendDirection(str, Enum):
    """Direction of a trend."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class TrendStrength(str, Enum):
    """Strength of a trend."""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


@dataclass
class TrendMetric:
    """Individual trend metric with analysis."""
    name: str
    values: List[Decimal]
    periods: List[str]
    growth_rate: Optional[Decimal]  # Period-over-period average growth
    direction: TrendDirection
    strength: TrendStrength
    volatility: Decimal  # Coefficient of variation
    seasonal_pattern: Optional[Dict[str, Decimal]] = None
    forecast_next: Optional[Decimal] = None
    confidence: Decimal = Decimal("0")  # 0-1 confidence in analysis

    @property
    def latest_value(self) -> Optional[Decimal]:
        """Get the most recent value."""
        return self.values[-1] if self.values else None

    @property
    def change_from_previous(self) -> Optional[Decimal]:
        """Get change from previous period."""
        if len(self.values) >= 2:
            return self.values[-1] - self.values[-2]
        return None

    @property
    def percent_change_from_previous(self) -> Optional[Decimal]:
        """Get percentage change from previous period."""
        if len(self.values) >= 2 and self.values[-2] != 0:
            return (self.values[-1] - self.values[-2]) / abs(self.values[-2])
        return None


@dataclass
class TrendResult:
    """Complete trend analysis result."""
    metrics: Dict[str, TrendMetric]
    period_range: Tuple[str, str]  # (start_period, end_period)
    analysis_summary: Dict[str, Any]
    key_insights: List[str]
    recommendations: List[str]

    def get_metric(self, metric_name: str) -> Optional[TrendMetric]:
        """Get a specific trend metric."""
        return self.metrics.get(metric_name)

    def get_trending_up(self) -> List[TrendMetric]:
        """Get metrics with upward trends."""
        return [m for m in self.metrics.values() if m.direction == TrendDirection.INCREASING]

    def get_trending_down(self) -> List[TrendMetric]:
        """Get metrics with downward trends."""
        return [m for m in self.metrics.values() if m.direction == TrendDirection.DECREASING]

    def get_volatile_metrics(self) -> List[TrendMetric]:
        """Get highly volatile metrics."""
        return [m for m in self.metrics.values() if m.direction == TrendDirection.VOLATILE]


class TrendAnalyzer:
    """Advanced trend analysis for restaurant financial data."""

    def __init__(self):
        self.min_periods_for_trend = 3
        self.volatility_threshold = Decimal("0.15")  # 15% coefficient of variation
        self.growth_significance_threshold = Decimal("0.02")  # 2% growth threshold

    def analyze_trends(self, historical_statements: List[IncomeStatement]) -> TrendResult:
        """
        Perform comprehensive trend analysis on historical financial data.

        Args:
            historical_statements: List of income statements in chronological order

        Returns:
            Complete trend analysis with insights and recommendations
        """
        if len(historical_statements) < 2:
            raise ValueError("Need at least 2 periods for trend analysis")

        # Extract time series data
        time_series = self._extract_time_series(historical_statements)

        # Calculate trends for each metric
        trends = {}
        for metric_name, values_and_periods in time_series.items():
            values, periods = values_and_periods
            if len(values) >= 2:  # Need at least 2 points for trend
                trends[metric_name] = self._analyze_metric_trend(metric_name, values, periods)

        # Generate analysis summary
        analysis_summary = self._generate_analysis_summary(trends)

        # Generate insights and recommendations
        insights = self._generate_insights(trends, historical_statements)
        recommendations = self._generate_recommendations(trends, historical_statements)

        period_range = (
            historical_statements[0].period.period_id,
            historical_statements[-1].period.period_id
        )

        return TrendResult(
            metrics=trends,
            period_range=period_range,
            analysis_summary=analysis_summary,
            key_insights=insights,
            recommendations=recommendations
        )

    def _extract_time_series(self, statements: List[IncomeStatement]) -> Dict[str, Tuple[List[Decimal], List[str]]]:
        """Extract time series data from income statements."""
        series = {}

        for statement in statements:
            period_id = statement.period.period_id

            # Revenue metrics
            self._add_to_series(series, "total_revenue", statement.revenue.total_revenue, period_id)
            self._add_to_series(series, "food_revenue", statement.revenue.food_revenue, period_id)
            self._add_to_series(series, "beverage_revenue", statement.revenue.beverage_revenue, period_id)

            # Cost metrics
            self._add_to_series(series, "total_cogs", statement.costs.total_cogs, period_id)
            self._add_to_series(series, "food_cost", statement.costs.food_cost, period_id)

            # Expense metrics
            self._add_to_series(series, "labor_cost", statement.expenses.labor_cost, period_id)
            self._add_to_series(series, "rent_expense", statement.expenses.rent_expense, period_id)

            # Profitability metrics
            self._add_to_series(series, "gross_profit", statement.metrics.gross_profit, period_id)
            self._add_to_series(series, "gross_margin", statement.metrics.gross_margin, period_id)
            self._add_to_series(series, "operating_profit", statement.metrics.operating_profit, period_id)

            # Ratio metrics
            if statement.metrics.food_cost_ratio:
                self._add_to_series(series, "food_cost_ratio", statement.metrics.food_cost_ratio, period_id)
            if statement.metrics.labor_cost_ratio:
                self._add_to_series(series, "labor_cost_ratio", statement.metrics.labor_cost_ratio, period_id)

        return series

    def _add_to_series(self, series: Dict, name: str, value: Decimal, period: str):
        """Add a value to a time series."""
        if name not in series:
            series[name] = ([], [])
        series[name][0].append(value)
        series[name][1].append(period)

    def _analyze_metric_trend(self, metric_name: str, values: List[Decimal], periods: List[str]) -> TrendMetric:
        """Analyze trend for a single metric."""
        # Calculate growth rate
        growth_rate = self._calculate_average_growth_rate(values)

        # Determine trend direction
        direction = self._determine_trend_direction(values, growth_rate)

        # Calculate volatility (coefficient of variation)
        volatility = self._calculate_volatility(values)

        # Determine trend strength
        strength = self._determine_trend_strength(growth_rate, volatility)

        # Detect seasonal patterns (if enough data)
        seasonal_pattern = self._detect_seasonal_pattern(values, periods) if len(values) >= 12 else None

        # Forecast next period
        forecast_next = self._forecast_next_period(values, growth_rate, seasonal_pattern)

        # Calculate confidence
        confidence = self._calculate_confidence(values, volatility, len(values))

        return TrendMetric(
            name=metric_name,
            values=values,
            periods=periods,
            growth_rate=growth_rate,
            direction=direction,
            strength=strength,
            volatility=volatility,
            seasonal_pattern=seasonal_pattern,
            forecast_next=forecast_next,
            confidence=confidence
        )

    def _calculate_average_growth_rate(self, values: List[Decimal]) -> Optional[Decimal]:
        """Calculate average period-over-period growth rate."""
        if len(values) < 2:
            return None

        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                growth_rate = (values[i] - values[i-1]) / abs(values[i-1])
                growth_rates.append(growth_rate)

        if not growth_rates:
            return None

        # Use geometric mean for more accurate average growth rate
        if len(growth_rates) == 1:
            return growth_rates[0]

        # Convert to compound growth rate
        product = Decimal("1")
        for rate in growth_rates:
            product *= (Decimal("1") + rate)

        if product <= 0:
            return None

        # Calculate geometric mean
        avg_growth = product ** (Decimal("1") / Decimal(str(len(growth_rates)))) - Decimal("1")
        return avg_growth

    def _determine_trend_direction(self, values: List[Decimal], growth_rate: Optional[Decimal]) -> TrendDirection:
        """Determine the overall trend direction."""
        if growth_rate is None:
            return TrendDirection.STABLE

        # Check volatility first
        volatility = self._calculate_volatility(values)
        if volatility > self.volatility_threshold:
            return TrendDirection.VOLATILE

        # Check growth significance
        if abs(growth_rate) < self.growth_significance_threshold:
            return TrendDirection.STABLE
        elif growth_rate > 0:
            return TrendDirection.INCREASING
        else:
            return TrendDirection.DECREASING

    def _calculate_volatility(self, values: List[Decimal]) -> Decimal:
        """Calculate coefficient of variation as a measure of volatility."""
        if len(values) < 2:
            return Decimal("0")

        # Convert to float for statistics calculation
        float_values = [float(v) for v in values]

        try:
            mean = statistics.mean(float_values)
            if mean == 0:
                return Decimal("0")

            stdev = statistics.stdev(float_values)
            cv = Decimal(str(stdev)) / Decimal(str(abs(mean)))
            return cv
        except (statistics.StatisticsError, ValueError):
            return Decimal("0")

    def _determine_trend_strength(self, growth_rate: Optional[Decimal], volatility: Decimal) -> TrendStrength:
        """Determine the strength of the trend."""
        if growth_rate is None:
            return TrendStrength.WEAK

        abs_growth = abs(growth_rate)

        # Strong trend: high growth rate and low volatility
        if abs_growth >= Decimal("0.1") and volatility <= Decimal("0.1"):
            return TrendStrength.STRONG
        # Moderate trend: moderate growth or moderate volatility
        elif abs_growth >= Decimal("0.05") and volatility <= Decimal("0.2"):
            return TrendStrength.MODERATE
        else:
            return TrendStrength.WEAK

    def _detect_seasonal_pattern(self, values: List[Decimal], periods: List[str]) -> Optional[Dict[str, Decimal]]:
        """Detect seasonal patterns in the data."""
        if len(values) < 12:  # Need at least a year of data
            return None

        # Simple seasonal analysis - group by month/quarter
        seasonal_groups = {}

        for value, period in zip(values, periods):
            # Extract month or quarter from period
            season_key = self._extract_season_key(period)
            if season_key:
                if season_key not in seasonal_groups:
                    seasonal_groups[season_key] = []
                seasonal_groups[season_key].append(value)

        # Calculate average for each season
        seasonal_averages = {}
        for season, season_values in seasonal_groups.items():
            if len(season_values) >= 2:  # Need multiple observations
                avg_value = sum(season_values) / len(season_values)
                seasonal_averages[season] = avg_value

        return seasonal_averages if len(seasonal_averages) >= 3 else None

    def _extract_season_key(self, period: str) -> Optional[str]:
        """Extract seasonal key from period string."""
        # Handle Chinese month format
        if "月" in period:
            month_map = {
                "1月": "Q1", "2月": "Q1", "3月": "Q1",
                "4月": "Q2", "5月": "Q2", "6月": "Q2",
                "7月": "Q3", "8月": "Q3", "9月": "Q3",
                "10月": "Q4", "11月": "Q4", "12月": "Q4"
            }
            for month, quarter in month_map.items():
                if month in period:
                    return quarter

        # Handle quarter format
        if "Q" in period:
            return period.split("Q")[1][:1] if "Q" in period else None

        return None

    def _forecast_next_period(self, values: List[Decimal], growth_rate: Optional[Decimal], seasonal_pattern: Optional[Dict[str, Decimal]]) -> Optional[Decimal]:
        """Forecast the next period value."""
        if not values or growth_rate is None:
            return None

        latest_value = values[-1]

        # Simple forecast based on growth rate
        base_forecast = latest_value * (Decimal("1") + growth_rate)

        # Adjust for seasonality if available
        if seasonal_pattern:
            # This is a simplified seasonal adjustment
            # In practice, you'd need more sophisticated seasonal decomposition
            avg_seasonal_factor = sum(seasonal_pattern.values()) / len(seasonal_pattern.values())
            # Apply a small seasonal adjustment (simplified)
            base_forecast *= (avg_seasonal_factor / latest_value) if latest_value != 0 else Decimal("1")

        return base_forecast

    def _calculate_confidence(self, values: List[Decimal], volatility: Decimal, data_points: int) -> Decimal:
        """Calculate confidence in the trend analysis."""
        # Base confidence on data points and volatility
        data_confidence = min(Decimal(str(data_points)) / Decimal("12"), Decimal("1"))  # Max confidence at 12+ points
        volatility_confidence = max(Decimal("0"), Decimal("1") - volatility)

        # Combined confidence (weighted average)
        confidence = (data_confidence * Decimal("0.4") + volatility_confidence * Decimal("0.6"))
        return min(confidence, Decimal("1"))

    def _generate_analysis_summary(self, trends: Dict[str, TrendMetric]) -> Dict[str, Any]:
        """Generate summary statistics for the trend analysis."""
        summary = {
            "total_metrics_analyzed": len(trends),
            "trending_up": len([t for t in trends.values() if t.direction == TrendDirection.INCREASING]),
            "trending_down": len([t for t in trends.values() if t.direction == TrendDirection.DECREASING]),
            "stable": len([t for t in trends.values() if t.direction == TrendDirection.STABLE]),
            "volatile": len([t for t in trends.values() if t.direction == TrendDirection.VOLATILE]),
            "high_confidence": len([t for t in trends.values() if t.confidence > Decimal("0.7")]),
            "average_confidence": Decimal("0")
        }

        if trends:
            avg_confidence = sum(t.confidence for t in trends.values()) / len(trends)
            summary["average_confidence"] = avg_confidence

        return summary

    def _generate_insights(self, trends: Dict[str, TrendMetric], statements: List[IncomeStatement]) -> List[str]:
        """Generate key insights from trend analysis."""
        insights = []

        # Revenue insights
        revenue_trend = trends.get("total_revenue")
        if revenue_trend:
            if revenue_trend.direction == TrendDirection.INCREASING:
                insights.append(f"Revenue is growing at an average rate of {revenue_trend.growth_rate:.1%} per period")
            elif revenue_trend.direction == TrendDirection.DECREASING:
                insights.append(f"Revenue is declining at an average rate of {abs(revenue_trend.growth_rate):.1%} per period")

        # Cost trends
        food_cost_trend = trends.get("food_cost_ratio")
        if food_cost_trend and food_cost_trend.direction == TrendDirection.INCREASING:
            insights.append("Food cost ratio is increasing, indicating potential cost control issues")

        labor_cost_trend = trends.get("labor_cost_ratio")
        if labor_cost_trend and labor_cost_trend.direction == TrendDirection.INCREASING:
            insights.append("Labor cost ratio is trending upward, consider operational efficiency improvements")

        # Profitability insights
        margin_trend = trends.get("gross_margin")
        if margin_trend:
            if margin_trend.direction == TrendDirection.DECREASING:
                insights.append("Gross margins are declining, review pricing and cost management strategies")
            elif margin_trend.direction == TrendDirection.INCREASING:
                insights.append("Gross margins are improving, indicating effective cost management")

        # Volatility insights
        volatile_metrics = [name for name, trend in trends.items() if trend.direction == TrendDirection.VOLATILE]
        if len(volatile_metrics) > 3:
            insights.append(f"High volatility detected in {len(volatile_metrics)} metrics, indicating operational inconsistency")

        return insights

    def _generate_recommendations(self, trends: Dict[str, TrendMetric], statements: List[IncomeStatement]) -> List[str]:
        """Generate actionable recommendations based on trends."""
        recommendations = []

        # Revenue recommendations
        revenue_trend = trends.get("total_revenue")
        if revenue_trend and revenue_trend.direction == TrendDirection.DECREASING:
            recommendations.append("Focus on revenue recovery: consider menu optimization, marketing campaigns, or service improvements")

        # Cost control recommendations
        food_cost_trend = trends.get("food_cost_ratio")
        if food_cost_trend and food_cost_trend.direction == TrendDirection.INCREASING:
            recommendations.append("Implement stronger food cost controls: review portion sizes, supplier contracts, and waste management")

        labor_trend = trends.get("labor_cost_ratio")
        if labor_trend and labor_trend.direction == TrendDirection.INCREASING:
            recommendations.append("Optimize labor efficiency: review scheduling, training, and productivity metrics")

        # Profitability recommendations
        margin_trend = trends.get("gross_margin")
        if margin_trend and margin_trend.direction == TrendDirection.DECREASING:
            recommendations.append("Protect margins: review menu pricing, negotiate with suppliers, and reduce waste")

        # Volatility recommendations
        volatile_count = len([t for t in trends.values() if t.direction == TrendDirection.VOLATILE])
        if volatile_count > len(trends) * 0.3:  # More than 30% volatile
            recommendations.append("Establish more consistent operational procedures to reduce performance volatility")

        # Growth opportunity recommendations
        growth_metrics = [t for t in trends.values() if t.direction == TrendDirection.INCREASING and t.strength == TrendStrength.STRONG]
        if len(growth_metrics) >= 2:
            recommendations.append("Capitalize on positive trends: consider expansion or investment in successful areas")

        return recommendations

    def calculate_compound_growth_rate(self, values: List[Decimal], periods: int = None) -> Optional[Decimal]:
        """Calculate compound annual growth rate (CAGR) or compound period growth rate."""
        if len(values) < 2:
            return None

        periods = periods or (len(values) - 1)
        start_value = values[0]
        end_value = values[-1]

        if start_value <= 0:
            return None

        # CAGR = (End Value / Start Value)^(1/periods) - 1
        try:
            ratio = end_value / start_value
            if ratio <= 0:
                return None

            cagr = (ratio ** (Decimal("1") / Decimal(str(periods)))) - Decimal("1")
            return cagr
        except (ValueError, OverflowError):
            return None

    def detect_anomalies(self, values: List[Decimal], threshold: Decimal = Decimal("2.0")) -> List[int]:
        """Detect anomalous values using statistical methods."""
        if len(values) < 3:
            return []

        # Convert to floats for calculation
        float_values = [float(v) for v in values]

        try:
            mean = statistics.mean(float_values)
            stdev = statistics.stdev(float_values)

            if stdev == 0:
                return []

            anomalies = []
            for i, value in enumerate(float_values):
                z_score = abs(value - mean) / stdev
                if z_score > float(threshold):
                    anomalies.append(i)

            return anomalies
        except statistics.StatisticsError:
            return []