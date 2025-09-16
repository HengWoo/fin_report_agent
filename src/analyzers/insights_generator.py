"""
Financial Insights Generator for Restaurant Analytics

This module generates actionable business insights from financial analysis,
combining KPIs, trends, and comparative data into meaningful recommendations.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
import logging

from ..models.financial_data import IncomeStatement, ValidationResult, DataQualityScore
from .kpi_calculator import KPICalculator, RestaurantKPIs, KPIMetric, KPICategory
from .trend_analyzer import TrendAnalyzer, TrendResult, TrendDirection, TrendStrength
from .comparative_analyzer import ComparativeAnalyzer, ComparisonResult

logger = logging.getLogger(__name__)


class InsightType(str, Enum):
    """Types of financial insights."""
    PERFORMANCE = "performance"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TREND = "trend"
    COMPARISON = "comparison"
    OPERATIONAL = "operational"


class Priority(str, Enum):
    """Priority levels for insights."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionType(str, Enum):
    """Types of recommended actions."""
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    STRATEGIC = "strategic"
    MONITORING = "monitoring"


@dataclass
class FinancialInsight:
    """Individual financial insight with actionable recommendations."""
    title: str
    description: str
    insight_type: InsightType
    priority: Priority
    confidence: Decimal  # 0-1 confidence score
    impact_potential: Decimal  # 0-1 potential business impact
    supporting_data: Dict[str, Any]
    recommendations: List[str]
    action_type: ActionType
    timeline: str  # Implementation timeline
    success_metrics: List[str]  # How to measure success
    chinese_summary: Optional[str] = None

    def format_for_display(self) -> str:
        """Format insight for display."""
        priority_emoji = "🔴" if self.priority == Priority.HIGH else "🟡" if self.priority == Priority.MEDIUM else "🟢"
        confidence_text = f"{self.confidence:.0%}"

        return f"{priority_emoji} {self.title}\n{self.description}\nConfidence: {confidence_text}\nRecommendations: {'; '.join(self.recommendations[:2])}"


@dataclass
class InsightSummary:
    """Summary of all generated insights."""
    insights: List[FinancialInsight]
    high_priority_count: int
    total_potential_impact: Decimal
    key_focus_areas: List[str]
    immediate_actions: List[str]
    strategic_recommendations: List[str]

    def get_insights_by_type(self, insight_type: InsightType) -> List[FinancialInsight]:
        """Get insights filtered by type."""
        return [insight for insight in self.insights if insight.insight_type == insight_type]

    def get_insights_by_priority(self, priority: Priority) -> List[FinancialInsight]:
        """Get insights filtered by priority."""
        return [insight for insight in self.insights if insight.priority == priority]


class InsightsGenerator:
    """Generator for comprehensive financial insights and recommendations."""

    def __init__(self):
        self.kpi_calculator = KPICalculator()
        self.trend_analyzer = TrendAnalyzer()
        self.comparative_analyzer = ComparativeAnalyzer()

    def generate_comprehensive_insights(
        self,
        current_statement: IncomeStatement,
        historical_statements: Optional[List[IncomeStatement]] = None,
        comparison_statements: Optional[List[IncomeStatement]] = None,
        validation_result: Optional[ValidationResult] = None,
        quality_score: Optional[DataQualityScore] = None
    ) -> InsightSummary:
        """
        Generate comprehensive financial insights from multiple analysis sources.

        Args:
            current_statement: Most recent financial statement
            historical_statements: Historical data for trend analysis
            comparison_statements: Peer restaurants for comparison
            validation_result: Data validation results
            quality_score: Data quality assessment

        Returns:
            Complete insight summary with prioritized recommendations
        """
        insights = []

        # Generate KPI-based insights
        kpi_insights = self._generate_kpi_insights(current_statement)
        insights.extend(kpi_insights)

        # Generate trend-based insights
        if historical_statements and len(historical_statements) >= 2:
            trend_insights = self._generate_trend_insights(historical_statements)
            insights.extend(trend_insights)

        # Generate comparative insights
        if comparison_statements:
            comparative_insights = self._generate_comparative_insights(current_statement, comparison_statements)
            insights.extend(comparative_insights)

        # Generate data quality insights
        if validation_result and quality_score:
            quality_insights = self._generate_quality_insights(validation_result, quality_score)
            insights.extend(quality_insights)

        # Generate operational insights
        operational_insights = self._generate_operational_insights(current_statement)
        insights.extend(operational_insights)

        # Prioritize and summarize
        prioritized_insights = self._prioritize_insights(insights)
        summary = self._create_insight_summary(prioritized_insights)

        return summary

    def _generate_kpi_insights(self, statement: IncomeStatement) -> List[FinancialInsight]:
        """Generate insights based on KPI analysis."""
        insights = []
        kpis = self.kpi_calculator.calculate_all_kpis(statement)

        # Analyze profitability
        profitability_insight = self._analyze_profitability_performance(kpis.profitability, statement)
        if profitability_insight:
            insights.append(profitability_insight)

        # Analyze cost control
        cost_control_insight = self._analyze_cost_control_performance(kpis.cost_control, statement)
        if cost_control_insight:
            insights.append(cost_control_insight)

        # Analyze efficiency
        efficiency_insight = self._analyze_efficiency_performance(kpis.efficiency, statement)
        if efficiency_insight:
            insights.append(efficiency_insight)

        # Analyze revenue mix
        revenue_mix_insight = self._analyze_revenue_mix_performance(kpis.revenue_mix, statement)
        if revenue_mix_insight:
            insights.append(revenue_mix_insight)

        return insights

    def _analyze_profitability_performance(self, profitability_kpis: Dict[str, KPIMetric], statement: IncomeStatement) -> Optional[FinancialInsight]:
        """Analyze profitability performance and generate insights."""
        gross_margin_metric = profitability_kpis.get("gross_profit_margin")
        if not gross_margin_metric:
            return None

        gross_margin = gross_margin_metric.value
        performance_status = gross_margin_metric.performance_status

        if performance_status == "poor":
            return FinancialInsight(
                title="Critical Profitability Concern",
                description=f"Gross margin of {gross_margin:.1%} is below healthy restaurant levels (55-75%). This indicates significant challenges with pricing or cost management.",
                insight_type=InsightType.RISK,
                priority=Priority.HIGH,
                confidence=Decimal("0.9"),
                impact_potential=Decimal("0.8"),
                supporting_data={
                    "gross_margin": gross_margin,
                    "benchmark_min": gross_margin_metric.benchmark_min,
                    "revenue": statement.revenue.total_revenue,
                    "cogs": statement.costs.total_cogs
                },
                recommendations=[
                    "Conduct immediate menu pricing review",
                    "Analyze cost structure and identify reduction opportunities",
                    "Review supplier contracts and negotiate better terms",
                    "Implement waste reduction programs"
                ],
                action_type=ActionType.IMMEDIATE,
                timeline="1-2 weeks",
                success_metrics=["Gross margin improvement", "Cost reduction percentage", "Revenue optimization"],
                chinese_summary="毛利率过低，需要立即审查定价和成本管理策略"
            )

        elif performance_status == "excellent":
            return FinancialInsight(
                title="Strong Profitability Position",
                description=f"Excellent gross margin of {gross_margin:.1%} indicates effective cost management and pricing strategy.",
                insight_type=InsightType.PERFORMANCE,
                priority=Priority.LOW,
                confidence=Decimal("0.9"),
                impact_potential=Decimal("0.3"),
                supporting_data={
                    "gross_margin": gross_margin,
                    "benchmark_max": gross_margin_metric.benchmark_max
                },
                recommendations=[
                    "Maintain current cost control practices",
                    "Consider expansion opportunities",
                    "Share best practices across operations"
                ],
                action_type=ActionType.STRATEGIC,
                timeline="Ongoing",
                success_metrics=["Margin consistency", "Growth opportunities", "Operational scaling"],
                chinese_summary="毛利率表现优秀，应保持当前管理策略"
            )

        return None

    def _analyze_cost_control_performance(self, cost_control_kpis: Dict[str, KPIMetric], statement: IncomeStatement) -> Optional[FinancialInsight]:
        """Analyze cost control performance."""
        food_cost_metric = cost_control_kpis.get("food_cost_percentage")
        labor_cost_metric = cost_control_kpis.get("labor_cost_percentage")
        prime_cost_metric = cost_control_kpis.get("prime_cost_percentage")

        # Check for high prime cost
        if prime_cost_metric and prime_cost_metric.value > Decimal("0.70"):
            return FinancialInsight(
                title="High Prime Cost Alert",
                description=f"Prime cost of {prime_cost_metric.value:.1%} exceeds healthy levels (50-65%), indicating combined food and labor cost issues.",
                insight_type=InsightType.RISK,
                priority=Priority.HIGH,
                confidence=Decimal("0.85"),
                impact_potential=Decimal("0.7"),
                supporting_data={
                    "prime_cost": prime_cost_metric.value,
                    "food_cost": food_cost_metric.value if food_cost_metric else None,
                    "labor_cost": labor_cost_metric.value if labor_cost_metric else None
                },
                recommendations=[
                    "Implement comprehensive cost reduction program",
                    "Review both food costs and labor efficiency",
                    "Optimize menu engineering for better margins",
                    "Improve operational procedures to reduce waste"
                ],
                action_type=ActionType.IMMEDIATE,
                timeline="2-4 weeks",
                success_metrics=["Prime cost reduction", "Food cost ratio improvement", "Labor productivity increase"],
                chinese_summary="主要成本过高，需要同时控制食材和人工成本"
            )

        # Check for excellent cost control
        if (food_cost_metric and food_cost_metric.performance_status == "excellent" and
            labor_cost_metric and labor_cost_metric.performance_status == "excellent"):
            return FinancialInsight(
                title="Excellent Cost Management",
                description="Both food and labor costs are well-controlled, indicating strong operational efficiency.",
                insight_type=InsightType.PERFORMANCE,
                priority=Priority.LOW,
                confidence=Decimal("0.8"),
                impact_potential=Decimal("0.2"),
                supporting_data={
                    "food_cost": food_cost_metric.value,
                    "labor_cost": labor_cost_metric.value
                },
                recommendations=[
                    "Document and standardize current practices",
                    "Train staff on cost control procedures",
                    "Monitor for consistency over time"
                ],
                action_type=ActionType.MONITORING,
                timeline="Ongoing",
                success_metrics=["Cost control consistency", "Procedure standardization", "Staff training completion"],
                chinese_summary="成本控制优秀，应维持并标准化当前做法"
            )

        return None

    def _analyze_efficiency_performance(self, efficiency_kpis: Dict[str, KPIMetric], statement: IncomeStatement) -> Optional[FinancialInsight]:
        """Analyze operational efficiency performance."""
        revenue_per_labor = efficiency_kpis.get("revenue_per_labor_dollar")

        if revenue_per_labor and revenue_per_labor.value < Decimal("3.0"):
            return FinancialInsight(
                title="Labor Efficiency Opportunity",
                description=f"Revenue per labor dollar of {revenue_per_labor.value:.1f} indicates potential for improved labor productivity.",
                insight_type=InsightType.OPPORTUNITY,
                priority=Priority.MEDIUM,
                confidence=Decimal("0.7"),
                impact_potential=Decimal("0.5"),
                supporting_data={
                    "revenue_per_labor": revenue_per_labor.value,
                    "total_revenue": statement.revenue.total_revenue,
                    "labor_cost": statement.expenses.labor_cost
                },
                recommendations=[
                    "Review staff scheduling optimization",
                    "Implement cross-training programs",
                    "Analyze peak hours and staffing patterns",
                    "Consider workflow improvements"
                ],
                action_type=ActionType.SHORT_TERM,
                timeline="4-6 weeks",
                success_metrics=["Revenue per labor hour improvement", "Staff productivity metrics", "Customer service scores"],
                chinese_summary="人工效率有提升空间，需要优化排班和培训"
            )

        return None

    def _analyze_revenue_mix_performance(self, revenue_mix_kpis: Dict[str, KPIMetric], statement: IncomeStatement) -> Optional[FinancialInsight]:
        """Analyze revenue mix performance."""
        high_margin_mix = revenue_mix_kpis.get("high_margin_item_mix")

        if high_margin_mix and high_margin_mix.value < Decimal("0.15"):
            return FinancialInsight(
                title="Revenue Mix Optimization Opportunity",
                description=f"High-margin items represent only {high_margin_mix.value:.1%} of revenue. Increasing this mix could significantly improve profitability.",
                insight_type=InsightType.OPPORTUNITY,
                priority=Priority.MEDIUM,
                confidence=Decimal("0.6"),
                impact_potential=Decimal("0.4"),
                supporting_data={
                    "current_high_margin_mix": high_margin_mix.value,
                    "beverage_revenue": statement.revenue.beverage_revenue,
                    "dessert_revenue": statement.revenue.dessert_revenue,
                    "total_revenue": statement.revenue.total_revenue
                },
                recommendations=[
                    "Enhance beverage menu and promotion",
                    "Introduce high-margin dessert offerings",
                    "Train staff on upselling techniques",
                    "Review menu placement and design"
                ],
                action_type=ActionType.SHORT_TERM,
                timeline="3-4 weeks",
                success_metrics=["High-margin item sales increase", "Average ticket size improvement", "Staff upselling performance"],
                chinese_summary="高利润项目比例偏低，需要加强饮品和甜品销售"
            )

        return None

    def _generate_trend_insights(self, historical_statements: List[IncomeStatement]) -> List[FinancialInsight]:
        """Generate insights based on trend analysis."""
        insights = []

        try:
            trend_result = self.trend_analyzer.analyze_trends(historical_statements)

            # Analyze revenue trends
            revenue_trend = trend_result.get_metric("total_revenue")
            if revenue_trend:
                revenue_insight = self._analyze_revenue_trend(revenue_trend)
                if revenue_insight:
                    insights.append(revenue_insight)

            # Analyze cost trends
            cost_trends_insight = self._analyze_cost_trends(trend_result)
            if cost_trends_insight:
                insights.append(cost_trends_insight)

            # Analyze volatility
            volatility_insight = self._analyze_volatility_patterns(trend_result)
            if volatility_insight:
                insights.append(volatility_insight)

        except Exception as e:
            logger.warning(f"Could not generate trend insights: {e}")

        return insights

    def _analyze_revenue_trend(self, revenue_trend) -> Optional[FinancialInsight]:
        """Analyze revenue trend patterns."""
        if revenue_trend.direction == TrendDirection.DECREASING and revenue_trend.strength in [TrendStrength.MODERATE, TrendStrength.STRONG]:
            return FinancialInsight(
                title="Revenue Decline Concern",
                description=f"Revenue has been declining at {abs(revenue_trend.growth_rate):.1%} per period. This trend requires immediate attention.",
                insight_type=InsightType.RISK,
                priority=Priority.HIGH,
                confidence=revenue_trend.confidence,
                impact_potential=Decimal("0.9"),
                supporting_data={
                    "growth_rate": revenue_trend.growth_rate,
                    "trend_strength": revenue_trend.strength.value,
                    "periods_analyzed": len(revenue_trend.values)
                },
                recommendations=[
                    "Conduct immediate market analysis",
                    "Review competitive positioning",
                    "Implement customer retention programs",
                    "Analyze service quality feedback"
                ],
                action_type=ActionType.IMMEDIATE,
                timeline="1-2 weeks",
                success_metrics=["Revenue growth reversal", "Customer acquisition rate", "Market share analysis"],
                chinese_summary="收入持续下降，需要立即分析原因并采取行动"
            )

        elif revenue_trend.direction == TrendDirection.INCREASING and revenue_trend.strength == TrendStrength.STRONG:
            return FinancialInsight(
                title="Strong Revenue Growth",
                description=f"Revenue is growing at {revenue_trend.growth_rate:.1%} per period. Consider strategies to sustain and accelerate this growth.",
                insight_type=InsightType.PERFORMANCE,
                priority=Priority.MEDIUM,
                confidence=revenue_trend.confidence,
                impact_potential=Decimal("0.6"),
                supporting_data={
                    "growth_rate": revenue_trend.growth_rate,
                    "trend_strength": revenue_trend.strength.value
                },
                recommendations=[
                    "Analyze growth drivers to replicate success",
                    "Consider capacity expansion",
                    "Invest in customer experience improvements",
                    "Explore new revenue streams"
                ],
                action_type=ActionType.STRATEGIC,
                timeline="1-3 months",
                success_metrics=["Sustained growth rate", "Capacity utilization", "Customer satisfaction scores"],
                chinese_summary="收入增长强劲，应分析成功因素并考虑扩展"
            )

        return None

    def _analyze_cost_trends(self, trend_result: TrendResult) -> Optional[FinancialInsight]:
        """Analyze cost trend patterns."""
        food_cost_trend = trend_result.get_metric("food_cost_ratio")
        labor_cost_trend = trend_result.get_metric("labor_cost_ratio")

        increasing_costs = []
        if food_cost_trend and food_cost_trend.direction == TrendDirection.INCREASING:
            increasing_costs.append("food costs")
        if labor_cost_trend and labor_cost_trend.direction == TrendDirection.INCREASING:
            increasing_costs.append("labor costs")

        if len(increasing_costs) >= 2:
            return FinancialInsight(
                title="Rising Cost Pressure",
                description=f"Both {' and '.join(increasing_costs)} are trending upward, putting pressure on profitability.",
                insight_type=InsightType.RISK,
                priority=Priority.HIGH,
                confidence=Decimal("0.8"),
                impact_potential=Decimal("0.7"),
                supporting_data={
                    "food_cost_trend": food_cost_trend.growth_rate if food_cost_trend else None,
                    "labor_cost_trend": labor_cost_trend.growth_rate if labor_cost_trend else None
                },
                recommendations=[
                    "Implement comprehensive cost monitoring",
                    "Review vendor relationships and contracts",
                    "Optimize operational procedures",
                    "Consider menu engineering adjustments"
                ],
                action_type=ActionType.IMMEDIATE,
                timeline="2-3 weeks",
                success_metrics=["Cost trend reversal", "Vendor cost negotiations", "Operational efficiency gains"],
                chinese_summary="成本持续上升，需要加强成本监控和优化"
            )

        return None

    def _analyze_volatility_patterns(self, trend_result: TrendResult) -> Optional[FinancialInsight]:
        """Analyze volatility in financial metrics."""
        volatile_metrics = trend_result.get_volatile_metrics()

        if len(volatile_metrics) > 3:  # High volatility across multiple metrics
            return FinancialInsight(
                title="Operational Inconsistency",
                description=f"High volatility detected in {len(volatile_metrics)} financial metrics, indicating inconsistent operations.",
                insight_type=InsightType.OPERATIONAL,
                priority=Priority.MEDIUM,
                confidence=Decimal("0.7"),
                impact_potential=Decimal("0.5"),
                supporting_data={
                    "volatile_metric_count": len(volatile_metrics),
                    "volatile_metrics": [m.name for m in volatile_metrics[:3]]
                },
                recommendations=[
                    "Standardize operational procedures",
                    "Implement regular performance monitoring",
                    "Provide consistent staff training",
                    "Review process documentation"
                ],
                action_type=ActionType.SHORT_TERM,
                timeline="4-6 weeks",
                success_metrics=["Reduced metric volatility", "Process standardization", "Performance consistency"],
                chinese_summary="运营指标波动较大，需要标准化操作流程"
            )

        return None

    def _generate_comparative_insights(self, current_statement: IncomeStatement, comparison_statements: List[IncomeStatement]) -> List[FinancialInsight]:
        """Generate insights from comparative analysis."""
        insights = []

        try:
            comparison_result = self.comparative_analyzer.compare_restaurants(
                current_statement, comparison_statements
            )

            # Analyze competitive position
            competitive_insight = self._analyze_competitive_position(comparison_result)
            if competitive_insight:
                insights.append(competitive_insight)

            # Analyze improvement opportunities
            opportunity_insights = self._analyze_improvement_opportunities(comparison_result)
            insights.extend(opportunity_insights)

        except Exception as e:
            logger.warning(f"Could not generate comparative insights: {e}")

        return insights

    def _analyze_competitive_position(self, comparison_result: ComparisonResult) -> Optional[FinancialInsight]:
        """Analyze competitive positioning."""
        overall_score = comparison_result.overall_score

        if overall_score < 25:
            return FinancialInsight(
                title="Below-Average Competitive Position",
                description=f"Overall performance ranks in bottom quartile (score: {overall_score:.0f}) compared to peer restaurants.",
                insight_type=InsightType.RISK,
                priority=Priority.HIGH,
                confidence=Decimal("0.8"),
                impact_potential=Decimal("0.8"),
                supporting_data={
                    "overall_score": overall_score,
                    "peer_count": len(comparison_result.comparison_restaurants)
                },
                recommendations=[
                    "Conduct comprehensive competitive analysis",
                    "Identify best practices from top performers",
                    "Implement performance improvement program",
                    "Focus on key differentiators"
                ],
                action_type=ActionType.IMMEDIATE,
                timeline="1-2 weeks",
                success_metrics=["Competitive ranking improvement", "Performance gap reduction", "Best practice implementation"],
                chinese_summary="竞争力排名偏低，需要学习优秀同行的最佳实践"
            )

        elif overall_score > 75:
            return FinancialInsight(
                title="Strong Competitive Advantage",
                description=f"Top quartile performance (score: {overall_score:.0f}) indicates competitive advantages to leverage.",
                insight_type=InsightType.PERFORMANCE,
                priority=Priority.LOW,
                confidence=Decimal("0.8"),
                impact_potential=Decimal("0.4"),
                supporting_data={
                    "overall_score": overall_score,
                    "strengths": comparison_result.strengths[:3]
                },
                recommendations=[
                    "Document and standardize successful practices",
                    "Consider expansion opportunities",
                    "Share expertise with other locations",
                    "Maintain competitive advantages"
                ],
                action_type=ActionType.STRATEGIC,
                timeline="Ongoing",
                success_metrics=["Advantage sustainability", "Knowledge transfer", "Market position maintenance"],
                chinese_summary="竞争优势明显，应保持并扩大这些优势"
            )

        return None

    def _analyze_improvement_opportunities(self, comparison_result: ComparisonResult) -> List[FinancialInsight]:
        """Analyze specific improvement opportunities from comparison."""
        insights = []

        # Focus on top improvement opportunities
        opportunities = comparison_result.improvement_opportunities[:2]  # Top 2

        for opp in opportunities:
            insights.append(FinancialInsight(
                title=f"Improvement Opportunity: {opp['metric'].replace('_', ' ').title()}",
                description=f"Potential to improve {opp['metric']} from current rank #{opp['current_rank']} to top quartile performance.",
                insight_type=InsightType.OPPORTUNITY,
                priority=Priority.MEDIUM,
                confidence=Decimal("0.6"),
                impact_potential=Decimal("0.5"),
                supporting_data=opp,
                recommendations=opp.get('actions', [])[:3],
                action_type=ActionType.SHORT_TERM,
                timeline="4-8 weeks",
                success_metrics=[f"{opp['metric']} improvement", "Competitive ranking increase", "Performance gap closure"],
                chinese_summary=f"在{opp['metric']}方面有改进机会，可提升竞争排名"
            ))

        return insights

    def _generate_quality_insights(self, validation_result: ValidationResult, quality_score: DataQualityScore) -> List[FinancialInsight]:
        """Generate insights from data quality analysis."""
        insights = []

        if quality_score.overall_score < 0.6:
            insights.append(FinancialInsight(
                title="Data Quality Concerns",
                description=f"Data quality score of {quality_score.overall_score:.1%} indicates potential accuracy issues that may affect analysis reliability.",
                insight_type=InsightType.OPERATIONAL,
                priority=Priority.MEDIUM,
                confidence=Decimal("0.9"),
                impact_potential=Decimal("0.3"),
                supporting_data={
                    "quality_score": quality_score.overall_score,
                    "missing_fields": quality_score.missing_fields,
                    "suspicious_values": quality_score.suspicious_values
                },
                recommendations=[
                    "Review data collection procedures",
                    "Implement data validation checks",
                    "Train staff on accurate record keeping",
                    "Establish regular data quality reviews"
                ],
                action_type=ActionType.SHORT_TERM,
                timeline="2-3 weeks",
                success_metrics=["Data quality score improvement", "Reduced validation errors", "Process standardization"],
                chinese_summary="数据质量需要改善，以确保分析的准确性"
            ))

        return insights

    def _generate_operational_insights(self, statement: IncomeStatement) -> List[FinancialInsight]:
        """Generate operational insights."""
        insights = []

        # Check for seasonal opportunities (if period indicates month)
        if "月" in statement.period.period_id:
            seasonal_insight = self._analyze_seasonal_opportunities(statement)
            if seasonal_insight:
                insights.append(seasonal_insight)

        return insights

    def _analyze_seasonal_opportunities(self, statement: IncomeStatement) -> Optional[FinancialInsight]:
        """Analyze seasonal business opportunities."""
        period = statement.period.period_id

        # Identify potential seasonal factors
        if any(month in period for month in ["12月", "1月", "2月"]):
            return FinancialInsight(
                title="Winter Season Optimization",
                description="Winter period presents opportunities for comfort food promotions and holiday marketing.",
                insight_type=InsightType.OPPORTUNITY,
                priority=Priority.LOW,
                confidence=Decimal("0.5"),
                impact_potential=Decimal("0.3"),
                supporting_data={"period": period},
                recommendations=[
                    "Introduce seasonal menu items",
                    "Plan holiday promotions",
                    "Adjust marketing for winter preferences",
                    "Consider delivery/takeout emphasis"
                ],
                action_type=ActionType.SHORT_TERM,
                timeline="2-4 weeks",
                success_metrics=["Seasonal sales increase", "Customer engagement", "Marketing ROI"],
                chinese_summary="冬季营销机会，可推出应季菜品和促销活动"
            )

        return None

    def _prioritize_insights(self, insights: List[FinancialInsight]) -> List[FinancialInsight]:
        """Prioritize insights based on priority, impact, and confidence."""
        def priority_score(insight: FinancialInsight) -> float:
            priority_weights = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
            return (
                priority_weights[insight.priority] * 10 +
                float(insight.impact_potential) * 5 +
                float(insight.confidence) * 2
            )

        return sorted(insights, key=priority_score, reverse=True)

    def _create_insight_summary(self, insights: List[FinancialInsight]) -> InsightSummary:
        """Create comprehensive insight summary."""
        high_priority_count = len([i for i in insights if i.priority == Priority.HIGH])
        total_impact = sum(i.impact_potential for i in insights)

        # Identify key focus areas
        focus_areas = []
        area_counts = {}
        for insight in insights[:5]:  # Top 5 insights
            area = insight.insight_type.value
            area_counts[area] = area_counts.get(area, 0) + 1

        focus_areas = [area for area, count in area_counts.items() if count >= 2]

        # Extract immediate actions
        immediate_actions = []
        for insight in insights:
            if insight.action_type == ActionType.IMMEDIATE:
                immediate_actions.extend(insight.recommendations[:2])

        # Extract strategic recommendations
        strategic_recommendations = []
        for insight in insights:
            if insight.action_type == ActionType.STRATEGIC:
                strategic_recommendations.extend(insight.recommendations[:2])

        return InsightSummary(
            insights=insights,
            high_priority_count=high_priority_count,
            total_potential_impact=total_impact,
            key_focus_areas=focus_areas[:3],
            immediate_actions=immediate_actions[:5],
            strategic_recommendations=strategic_recommendations[:5]
        )