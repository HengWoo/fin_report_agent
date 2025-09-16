"""Financial Analysis Package"""

from .kpi_calculator import KPICalculator, RestaurantKPIs
from .trend_analyzer import TrendAnalyzer, TrendResult
from .comparative_analyzer import ComparativeAnalyzer, ComparisonResult
from .insights_generator import InsightsGenerator, FinancialInsight

__all__ = [
    "KPICalculator",
    "RestaurantKPIs",
    "TrendAnalyzer",
    "TrendResult",
    "ComparativeAnalyzer",
    "ComparisonResult",
    "InsightsGenerator",
    "FinancialInsight"
]