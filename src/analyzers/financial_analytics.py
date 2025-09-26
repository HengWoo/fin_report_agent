"""
Financial Analytics Engine

This module provides comprehensive financial analytics by combining all analysis components
into a unified analytical framework for general business financial data.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from decimal import Decimal
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from ..models.financial_data import IncomeStatement, ValidationResult, DataQualityScore
from ..transformers.data_transformer import DataTransformer, TransformationResult
from .kpi_calculator import KPICalculator, RestaurantKPIs
from .trend_analyzer import TrendAnalyzer, TrendResult
from .comparative_analyzer import ComparativeAnalyzer, ComparisonResult
from .insights_generator import InsightsGenerator, InsightSummary, FinancialInsight

logger = logging.getLogger(__name__)


@dataclass
class BusinessPerformanceMetrics:
    """Comprehensive business performance metrics."""
    # Financial health indicators
    financial_health_score: Decimal  # 0-100 overall health score
    profitability_grade: str  # A, B, C, D, F
    efficiency_grade: str
    cost_control_grade: str

    # Key ratios
    prime_cost_ratio: Decimal
    revenue_per_unit: Optional[Decimal]  # Revenue efficiency metric
    customer_acquisition_cost: Optional[Decimal]

    # Operational metrics
    operational_efficiency_indicator: Decimal  # General efficiency measure
    staff_productivity_score: Decimal
    operational_performance_score: Decimal

    # Growth metrics
    revenue_growth_rate: Optional[Decimal]
    profit_growth_rate: Optional[Decimal]
    customer_growth_rate: Optional[Decimal]

    # Risk indicators
    cash_flow_risk: str  # Low, Medium, High
    cost_inflation_risk: str
    competitive_risk: str


@dataclass
class FinancialAnalysisReport:
    """Complete financial analysis report."""
    business_name: str
    analysis_date: str
    period_analyzed: str

    # Core analysis results
    kpis: RestaurantKPIs  # Will be renamed to BusinessKPIs in future
    performance_metrics: BusinessPerformanceMetrics
    insights: InsightSummary

    # Executive summary
    executive_summary: Dict[str, str]
    action_plan: List[Dict[str, Any]]

    # Optional components
    trend_analysis: Optional[TrendResult] = None
    competitive_analysis: Optional[ComparisonResult] = None
    data_quality: Optional[DataQualityScore] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return asdict(self)


class FinancialAnalyticsEngine:
    """Comprehensive analytics engine for general business financial analysis."""

    def __init__(self):
        self.data_transformer = DataTransformer()
        self.kpi_calculator = KPICalculator()
        self.trend_analyzer = TrendAnalyzer()
        self.comparative_analyzer = ComparativeAnalyzer()
        self.insights_generator = InsightsGenerator()

        # General business industry benchmarks (configurable)
        self.industry_benchmarks = {
            "service_business": {
                "gross_margin": {"excellent": 0.70, "good": 0.60, "poor": 0.45},
                "operating_cost_ratio": {"excellent": 0.28, "good": 0.32, "poor": 0.40},
                "labor_cost_ratio": {"excellent": 0.25, "good": 0.30, "poor": 0.40},
                "prime_cost_ratio": {"excellent": 0.55, "good": 0.62, "poor": 0.75}
            },
            "retail_business": {
                "gross_margin": {"excellent": 0.65, "good": 0.55, "poor": 0.40},
                "operating_cost_ratio": {"excellent": 0.30, "good": 0.35, "poor": 0.45},
                "labor_cost_ratio": {"excellent": 0.28, "good": 0.32, "poor": 0.42},
                "prime_cost_ratio": {"excellent": 0.58, "good": 0.67, "poor": 0.80}
            },
            "manufacturing": {
                "gross_margin": {"excellent": 0.60, "good": 0.50, "poor": 0.35},
                "operating_cost_ratio": {"excellent": 0.32, "good": 0.38, "poor": 0.48},
                "labor_cost_ratio": {"excellent": 0.35, "good": 0.40, "poor": 0.50},
                "prime_cost_ratio": {"excellent": 0.67, "good": 0.78, "poor": 0.90}
            }
        }

    def analyze_business_excel(self, excel_path: str) -> FinancialAnalysisReport:
        """
        Perform comprehensive financial analysis from Excel file.

        Args:
            excel_path: Path to business financial Excel file

        Returns:
            Complete financial analysis report
        """
        # Transform Excel data
        transformation_result = self.data_transformer.transform_excel_file(excel_path)

        if not transformation_result.success:
            raise ValueError(f"Failed to process Excel file: {'; '.join(transformation_result.errors)}")

        return self.analyze_business_statement(
            transformation_result.income_statement,
            validation_result=transformation_result.validation_result,
            quality_score=transformation_result.quality_score
        )

    def analyze_business_statement(
        self,
        income_statement: IncomeStatement,
        historical_statements: Optional[List[IncomeStatement]] = None,
        peer_statements: Optional[List[IncomeStatement]] = None,
        validation_result: Optional[ValidationResult] = None,
        quality_score: Optional[DataQualityScore] = None,
        business_type: str = "service_business"
    ) -> FinancialAnalysisReport:
        """
        Perform comprehensive business financial analysis.

        Args:
            income_statement: Current period financial statement
            historical_statements: Historical data for trend analysis
            peer_statements: Peer business data for comparison
            validation_result: Data validation results
            quality_score: Data quality assessment
            business_type: Type of business for benchmarking

        Returns:
            Complete financial analysis report
        """
        # Calculate KPIs
        kpis = self.kpi_calculator.calculate_all_kpis(income_statement)

        # Calculate business performance metrics
        performance_metrics = self._calculate_performance_metrics(
            income_statement, kpis, business_type
        )

        # Perform trend analysis if historical data available
        trend_analysis = None
        if historical_statements and len(historical_statements) >= 2:
            try:
                trend_analysis = self.trend_analyzer.analyze_trends(historical_statements)
            except Exception as e:
                logger.warning(f"Trend analysis failed: {e}")

        # Perform competitive analysis if peer data available
        competitive_analysis = None
        if peer_statements:
            try:
                competitive_analysis = self.comparative_analyzer.compare_restaurants(
                    income_statement, peer_statements
                )
            except Exception as e:
                logger.warning(f"Competitive analysis failed: {e}")

        # Generate comprehensive insights
        insights = self.insights_generator.generate_comprehensive_insights(
            income_statement,
            historical_statements,
            peer_statements,
            validation_result,
            quality_score
        )

        # Create executive summary
        executive_summary = self._create_executive_summary(
            performance_metrics, insights, trend_analysis, competitive_analysis
        )

        # Create action plan
        action_plan = self._create_action_plan(insights, performance_metrics)

        # Build final report
        business_name = income_statement.restaurant_name or "Business Analysis"

        return FinancialAnalysisReport(
            business_name=business_name,
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            period_analyzed=income_statement.period.period_id,
            kpis=kpis,
            performance_metrics=performance_metrics,
            insights=insights,
            trend_analysis=trend_analysis,
            competitive_analysis=competitive_analysis,
            data_quality=quality_score,
            executive_summary=executive_summary,
            action_plan=action_plan
        )

    def _calculate_performance_metrics(
        self,
        statement: IncomeStatement,
        kpis: RestaurantKPIs,
        business_type: str
    ) -> BusinessPerformanceMetrics:
        """Calculate comprehensive performance metrics."""

        # Calculate financial health score
        health_score = self._calculate_financial_health_score(kpis, business_type)

        # Calculate grades
        profitability_grade = self._calculate_grade(
            statement.metrics.gross_margin,
            self.industry_benchmarks[business_type]["gross_margin"]
        )

        efficiency_grade = self._calculate_efficiency_grade(kpis)
        cost_control_grade = self._calculate_cost_control_grade(kpis)

        # Calculate operational metrics
        operational_efficiency = self._estimate_operational_efficiency(statement)
        staff_productivity = self._calculate_staff_productivity_score(statement, kpis)
        operational_performance = self._calculate_operational_performance_score(statement)

        # Calculate risk indicators
        cash_flow_risk = self._assess_cash_flow_risk(statement)
        cost_inflation_risk = self._assess_cost_inflation_risk(statement)
        competitive_risk = self._assess_competitive_risk(statement, kpis)

        return BusinessPerformanceMetrics(
            financial_health_score=health_score,
            profitability_grade=profitability_grade,
            efficiency_grade=efficiency_grade,
            cost_control_grade=cost_control_grade,
            prime_cost_ratio=statement.metrics.prime_cost_ratio or Decimal("0"),
            revenue_per_unit=None,  # Would need unit data
            customer_acquisition_cost=None,  # Would need marketing spend data
            operational_efficiency_indicator=operational_efficiency,
            staff_productivity_score=staff_productivity,
            operational_performance_score=operational_performance,
            revenue_growth_rate=None,  # Would need historical data
            profit_growth_rate=None,
            customer_growth_rate=None,
            cash_flow_risk=cash_flow_risk,
            cost_inflation_risk=cost_inflation_risk,
            competitive_risk=competitive_risk
        )

    def _calculate_financial_health_score(self, kpis: RestaurantKPIs, business_type: str) -> Decimal:
        """Calculate overall financial health score (0-100)."""
        scores = []
        weights = []

        # Profitability (40% weight)
        profitability_metrics = kpis.profitability
        if "gross_profit_margin" in profitability_metrics:
            margin = profitability_metrics["gross_profit_margin"].value
            benchmark = self.industry_benchmarks[business_type]["gross_margin"]
            score = self._score_against_benchmark(margin, benchmark, higher_better=True)
            scores.append(score)
            weights.append(0.4)

        # Cost Control (35% weight)
        cost_metrics = kpis.cost_control
        if "prime_cost_percentage" in cost_metrics:
            prime_cost = cost_metrics["prime_cost_percentage"].value
            benchmark = self.industry_benchmarks[business_type]["prime_cost_ratio"]
            score = self._score_against_benchmark(prime_cost, benchmark, higher_better=False)
            scores.append(score)
            weights.append(0.35)

        # Efficiency (25% weight)
        efficiency_metrics = kpis.efficiency
        if efficiency_metrics:
            # Average efficiency scores
            eff_scores = []
            for metric in efficiency_metrics.values():
                if metric.benchmark_min and metric.benchmark_max:
                    if metric.value >= metric.benchmark_max:
                        eff_scores.append(100)
                    elif metric.value >= metric.benchmark_min:
                        eff_scores.append(75)
                    else:
                        eff_scores.append(50)

            if eff_scores:
                avg_eff_score = sum(eff_scores) / len(eff_scores)
                scores.append(avg_eff_score)
                weights.append(0.25)

        # Calculate weighted average
        if scores and weights:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
            return Decimal(str(weighted_score))
        else:
            return Decimal("50")  # Neutral score if no data

    def _score_against_benchmark(self, value: Decimal, benchmark: Dict[str, float], higher_better: bool = True) -> float:
        """Score a value against benchmark thresholds."""
        excellent = Decimal(str(benchmark["excellent"]))
        good = Decimal(str(benchmark["good"]))
        poor = Decimal(str(benchmark["poor"]))

        if higher_better:
            if value >= excellent:
                return 90
            elif value >= good:
                return 70
            elif value >= poor:
                return 50
            else:
                return 25
        else:
            if value <= excellent:
                return 90
            elif value <= good:
                return 70
            elif value <= poor:
                return 50
            else:
                return 25

    def _calculate_grade(self, value: Decimal, benchmark: Dict[str, float]) -> str:
        """Calculate letter grade based on benchmark."""
        excellent = Decimal(str(benchmark["excellent"]))
        good = Decimal(str(benchmark["good"]))
        poor = Decimal(str(benchmark["poor"]))

        if value >= excellent:
            return "A"
        elif value >= good:
            return "B"
        elif value >= poor:
            return "C"
        else:
            return "D"

    def _calculate_efficiency_grade(self, kpis: RestaurantKPIs) -> str:
        """Calculate efficiency grade."""
        efficiency_metrics = kpis.efficiency

        if not efficiency_metrics:
            return "C"

        # Score based on performance status
        scores = []
        for metric in efficiency_metrics.values():
            status = metric.performance_status
            if status == "excellent":
                scores.append(4)
            elif status == "good":
                scores.append(3)
            elif status == "poor":
                scores.append(1)
            else:
                scores.append(2)

        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score >= 3.5:
                return "A"
            elif avg_score >= 2.5:
                return "B"
            elif avg_score >= 1.5:
                return "C"
            else:
                return "D"

        return "C"

    def _calculate_cost_control_grade(self, kpis: RestaurantKPIs) -> str:
        """Calculate cost control grade."""
        cost_metrics = kpis.cost_control

        if not cost_metrics:
            return "C"

        # Focus on key cost control metrics
        key_metrics = ["food_cost_percentage", "labor_cost_percentage", "prime_cost_percentage"]
        scores = []

        for metric_name in key_metrics:
            if metric_name in cost_metrics:
                metric = cost_metrics[metric_name]
                status = metric.performance_status
                if status == "excellent":
                    scores.append(4)
                elif status == "good":
                    scores.append(3)
                elif status == "poor":
                    scores.append(1)
                else:
                    scores.append(2)

        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score >= 3.5:
                return "A"
            elif avg_score >= 2.5:
                return "B"
            elif avg_score >= 1.5:
                return "C"
            else:
                return "D"

        return "C"

    def _estimate_operational_efficiency(self, statement: IncomeStatement) -> Decimal:
        """Estimate operational efficiency indicator based on cost patterns."""
        # Simple estimation based on operational cost efficiency
        if statement.revenue.total_revenue > 0 and statement.expenses.total_expenses > 0:
            expense_ratio = statement.expenses.total_expenses / statement.revenue.total_revenue

            # Lower expense ratio indicates better efficiency
            if expense_ratio < Decimal("0.3"):
                return Decimal("0.9")  # High efficiency
            elif expense_ratio < Decimal("0.5"):
                return Decimal("0.7")  # Good efficiency
            elif expense_ratio < Decimal("0.7"):
                return Decimal("0.5")  # Average efficiency
            else:
                return Decimal("0.3")  # Low efficiency

        return Decimal("0.5")  # Average assumption

    def _calculate_staff_productivity_score(self, statement: IncomeStatement, kpis: RestaurantKPIs) -> Decimal:
        """Calculate staff productivity score."""
        efficiency_metrics = kpis.efficiency

        if "revenue_per_labor_dollar" in efficiency_metrics:
            metric = efficiency_metrics["revenue_per_labor_dollar"]
            if metric.value >= Decimal("4.5"):
                return Decimal("0.9")
            elif metric.value >= Decimal("3.5"):
                return Decimal("0.7")
            elif metric.value >= Decimal("2.5"):
                return Decimal("0.5")
            else:
                return Decimal("0.3")

        return Decimal("0.5")  # Default

    def _calculate_operational_performance_score(self, statement: IncomeStatement) -> Decimal:
        """Calculate operational performance score based on revenue efficiency."""
        if statement.revenue.total_revenue <= 0:
            return Decimal("0.5")

        # Calculate performance based on revenue to cost efficiency
        if statement.costs.total_costs > 0:
            revenue_efficiency = statement.revenue.total_revenue / statement.costs.total_costs

            # Score based on revenue efficiency
            if revenue_efficiency >= Decimal("3.0"):
                return Decimal("0.9")
            elif revenue_efficiency >= Decimal("2.0"):
                return Decimal("0.7")
            elif revenue_efficiency >= Decimal("1.5"):
                return Decimal("0.5")
            else:
                return Decimal("0.3")

        return Decimal("0.5")

    def _assess_cash_flow_risk(self, statement: IncomeStatement) -> str:
        """Assess cash flow risk level."""
        if statement.metrics.operating_margin < Decimal("0.05"):
            return "High"
        elif statement.metrics.operating_margin < Decimal("0.10"):
            return "Medium"
        else:
            return "Low"

    def _assess_cost_inflation_risk(self, statement: IncomeStatement) -> str:
        """Assess cost inflation risk."""
        # Simple assessment based on current cost structure
        if statement.metrics.prime_cost_ratio and statement.metrics.prime_cost_ratio > Decimal("0.70"):
            return "High"
        elif statement.metrics.prime_cost_ratio and statement.metrics.prime_cost_ratio > Decimal("0.60"):
            return "Medium"
        else:
            return "Low"

    def _assess_competitive_risk(self, statement: IncomeStatement, kpis: RestaurantKPIs) -> str:
        """Assess competitive risk level."""
        # Based on overall performance
        performance_summary = kpis.get_performance_summary()

        poor_metrics = performance_summary.get("poor", 0)
        total_metrics = sum(performance_summary.values())

        if total_metrics > 0:
            poor_ratio = poor_metrics / total_metrics
            if poor_ratio > 0.3:
                return "High"
            elif poor_ratio > 0.1:
                return "Medium"
            else:
                return "Low"

        return "Medium"

    def _create_executive_summary(
        self,
        performance_metrics: BusinessPerformanceMetrics,
        insights: InsightSummary,
        trend_analysis: Optional[TrendResult],
        competitive_analysis: Optional[ComparisonResult]
    ) -> Dict[str, str]:
        """Create executive summary."""
        summary = {}

        # Financial health summary
        health_score = performance_metrics.financial_health_score
        if health_score >= 80:
            summary["financial_health"] = f"Excellent financial health (Score: {health_score:.0f}/100). Strong performance across key metrics."
        elif health_score >= 60:
            summary["financial_health"] = f"Good financial health (Score: {health_score:.0f}/100). Some areas for improvement identified."
        else:
            summary["financial_health"] = f"Concerning financial health (Score: {health_score:.0f}/100). Immediate attention required."

        # Key strengths and concerns
        high_priority_insights = insights.get_insights_by_priority("high")
        if high_priority_insights:
            summary["key_concerns"] = f"{len(high_priority_insights)} high-priority issues identified requiring immediate attention."
        else:
            summary["key_concerns"] = "No critical issues identified. Focus on optimization opportunities."

        # Performance grades summary
        summary["performance_overview"] = (
            f"Profitability: {performance_metrics.profitability_grade}, "
            f"Efficiency: {performance_metrics.efficiency_grade}, "
            f"Cost Control: {performance_metrics.cost_control_grade}"
        )

        # Trend summary
        if trend_analysis:
            improving_trends = len(trend_analysis.get_trending_up())
            declining_trends = len(trend_analysis.get_trending_down())
            summary["trend_analysis"] = f"{improving_trends} metrics improving, {declining_trends} declining over time."

        # Competitive position
        if competitive_analysis:
            overall_score = competitive_analysis.overall_score
            if overall_score >= 75:
                summary["competitive_position"] = f"Strong competitive position (Top 25% percentile)"
            elif overall_score >= 50:
                summary["competitive_position"] = f"Average competitive position ({overall_score:.0f}th percentile)"
            else:
                summary["competitive_position"] = f"Below-average competitive position ({overall_score:.0f}th percentile)"

        return summary

    def _create_action_plan(self, insights: InsightSummary, performance_metrics: BusinessPerformanceMetrics) -> List[Dict[str, Any]]:
        """Create prioritized action plan."""
        actions = []

        # Add immediate actions from high-priority insights
        high_priority_insights = insights.get_insights_by_priority("high")
        for insight in high_priority_insights[:3]:  # Top 3 high-priority
            actions.append({
                "priority": "immediate",
                "title": insight.title,
                "description": insight.description,
                "recommendations": insight.recommendations[:2],
                "timeline": insight.timeline,
                "success_metrics": insight.success_metrics
            })

        # Add strategic actions
        if performance_metrics.financial_health_score >= 70:
            actions.append({
                "priority": "strategic",
                "title": "Growth and Expansion Planning",
                "description": "Strong financial position enables strategic growth initiatives",
                "recommendations": [
                    "Evaluate expansion opportunities",
                    "Invest in customer experience enhancements",
                    "Consider new revenue streams"
                ],
                "timeline": "3-6 months",
                "success_metrics": ["Revenue growth", "Market expansion", "Customer satisfaction"]
            })

        # Add monitoring actions
        actions.append({
            "priority": "ongoing",
            "title": "Performance Monitoring",
            "description": "Establish regular monitoring of key performance indicators",
            "recommendations": [
                "Weekly KPI dashboard review",
                "Monthly financial analysis",
                "Quarterly competitive benchmarking"
            ],
            "timeline": "Ongoing",
            "success_metrics": ["Consistent monitoring", "Early issue detection", "Performance trends"]
        })

        return actions[:5]  # Limit to top 5 actions