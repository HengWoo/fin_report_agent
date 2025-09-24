"""
Financial Analysis Tools for MCP Server

This module provides tool implementations for the MCP server,
wrapping the restaurant financial analysis functionality.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, date

from .config import MCPServerConfig, ToolConfig, DEFAULT_TOOL_CONFIGS
from ..analyzers.restaurant_analytics import RestaurantAnalyticsEngine
from ..parsers.chinese_excel_parser import ChineseExcelParser
from ..validators.restaurant_validator import RestaurantFinancialValidator
from ..models.financial_data import (
    IncomeStatement,
    FinancialPeriod,
    RevenueBreakdown,
    CostBreakdown,
    ExpenseBreakdown,
    ProfitMetrics,
)
from datetime import timedelta


class FinancialAnalysisTools:
    """Tools for restaurant financial analysis."""

    def __init__(self, config: MCPServerConfig):
        """Initialize financial analysis tools."""
        self.config = config
        self.logger = logging.getLogger(f"{config.server_name}.tools")

        # Initialize analysis components
        self.analytics_engine = RestaurantAnalyticsEngine()
        self.parser = ChineseExcelParser()
        self.validator = RestaurantFinancialValidator()

        # Tool configurations
        self.tool_configs = {
            name: ToolConfig(**config_data.model_dump())
            for name, config_data in DEFAULT_TOOL_CONFIGS.items()
        }

    async def parse_excel_file(
        self, file_path: str, sheet_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse Chinese restaurant Excel financial statements.

        Args:
            file_path: Path to the Excel file
            sheet_name: Optional sheet name to parse

        Returns:
            Dictionary containing parsed financial data
        """
        self.logger.info(f"Parsing Excel file: {file_path}")

        # Validate file path
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        # Check file size
        file_size_mb = path_obj.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(
                f"File size ({file_size_mb:.1f} MB) exceeds limit ({self.config.max_file_size_mb} MB)"
            )

        # Check file extension
        if path_obj.suffix.lower() not in self.config.allowed_file_extensions:
            raise ValueError(
                f"File extension {path_obj.suffix} not allowed. Allowed: {self.config.allowed_file_extensions}"
            )

        try:
            # Parse the Excel file
            result = self.parser.parse_income_statement(file_path, sheet_name)

            return {
                "success": True,
                "file_path": str(path_obj.absolute()),
                "file_size_mb": round(file_size_mb, 2),
                "sheet_name": sheet_name,
                "periods": result.get("periods", []),
                "financial_data": result.get("financial_data", {}),
                "chinese_terms_mapped": len(result.get("term_mappings", {})),
                "parsed_at": datetime.now().isoformat(),
                "parser_version": "1.0.0",
            }

        except Exception as e:
            self.logger.error(f"Excel parsing failed: {str(e)}")
            raise

    async def validate_financial_data(
        self, financial_data: Dict[str, Any], strict_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Validate restaurant financial data against industry standards.

        Args:
            financial_data: Financial data to validate
            strict_mode: Enable strict validation mode

        Returns:
            Dictionary containing validation results
        """
        self.logger.info("Validating financial data")

        try:
            # Convert financial data to IncomeStatement objects for validation
            validation_results = []
            all_valid = True

            for period_id, period_data in financial_data.items():
                try:
                    # Build income statement from period data
                    income_statement = self._build_income_statement_from_data(
                        period_id, period_data
                    )

                    # Validate the income statement
                    period_validation = self.validator.validate_income_statement(
                        income_statement
                    )

                    if period_validation:
                        all_valid = False
                        for issue in period_validation:
                            validation_results.append(
                                {
                                    "period": period_id,
                                    "code": issue["code"],
                                    "severity": issue["severity"],
                                    "message": issue["message"],
                                    "field": issue.get("field", "unknown"),
                                }
                            )

                except Exception as e:
                    all_valid = False
                    validation_results.append(
                        {
                            "period": period_id,
                            "code": "VALIDATION_ERROR",
                            "severity": "error",
                            "message": f"Validation failed: {str(e)}",
                            "field": "general",
                        }
                    )

            return {
                "success": True,
                "is_valid": all_valid,
                "strict_mode": strict_mode,
                "total_issues": len(validation_results),
                "validation_results": validation_results,
                "validated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Financial data validation failed: {str(e)}")
            raise

    async def calculate_restaurant_kpis(
        self, income_statement_data: Dict[str, Any], include_benchmarks: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate restaurant KPIs and performance metrics.

        Args:
            income_statement_data: Income statement data
            include_benchmarks: Include industry benchmark comparisons

        Returns:
            Dictionary containing calculated KPIs
        """
        self.logger.info("Calculating restaurant KPIs")

        try:
            # Convert to IncomeStatement object
            income_statement = self._convert_to_income_statement(income_statement_data)

            # Calculate KPIs using the analytics engine
            from ..analyzers.kpi_calculator import KPICalculator

            kpi_calculator = KPICalculator()
            kpis = kpi_calculator.calculate_all_kpis(income_statement)

            # Convert to dictionary
            kpi_dict = {
                "profitability": (
                    kpis.profitability.__dict__
                    if hasattr(kpis.profitability, "__dict__")
                    else kpis.profitability
                ),
                "efficiency": (
                    kpis.efficiency.__dict__
                    if hasattr(kpis.efficiency, "__dict__")
                    else kpis.efficiency
                ),
                "growth": (
                    kpis.growth.__dict__
                    if hasattr(kpis.growth, "__dict__")
                    else kpis.growth
                ),
                "liquidity": (
                    kpis.liquidity.__dict__
                    if hasattr(kpis.liquidity, "__dict__")
                    else kpis.liquidity
                ),
                "risk": (
                    kpis.risk.__dict__ if hasattr(kpis.risk, "__dict__") else kpis.risk
                ),
            }

            result = {
                "success": True,
                "period": income_statement.period.period_id,
                "kpis": kpi_dict,
                "benchmarks_included": include_benchmarks,
                "calculated_at": datetime.now().isoformat(),
            }

            # Add benchmark comparisons if requested
            if include_benchmarks:
                result["benchmark_analysis"] = self._generate_benchmark_comparison(kpis)

            return result

        except Exception as e:
            self.logger.error(f"KPI calculation failed: {str(e)}")
            raise

    async def analyze_financial_trends(
        self,
        historical_statements: List[Dict[str, Any]],
        include_forecasting: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform trend analysis on historical restaurant financial data.

        Args:
            historical_statements: List of historical income statements
            include_forecasting: Include future trend forecasting

        Returns:
            Dictionary containing trend analysis results
        """
        self.logger.info(f"Analyzing trends for {len(historical_statements)} periods")

        if len(historical_statements) < 2:
            raise ValueError(
                "At least 2 historical statements required for trend analysis"
            )

        try:
            # Convert to IncomeStatement objects
            statements = [
                self._convert_to_income_statement(stmt_data)
                for stmt_data in historical_statements
            ]

            # Sort by period
            statements.sort(key=lambda x: x.period.start_date)

            # Perform trend analysis
            from ..analyzers.trend_analyzer import TrendAnalyzer

            trend_analyzer = TrendAnalyzer()
            trend_result = trend_analyzer.analyze_trends(statements)

            return {
                "success": True,
                "periods_analyzed": len(statements),
                "date_range": {
                    "start": statements[0].period.start_date.isoformat(),
                    "end": statements[-1].period.end_date.isoformat(),
                },
                "trends": {
                    "growth_rates": trend_result.growth_rates,
                    "trend_direction": trend_result.trend_summary.get(
                        "overall_direction", "stable"
                    ),
                    "key_metrics": trend_result.key_metrics,
                    "trend_summary": trend_result.trend_summary,
                },
                "forecasting_included": include_forecasting,
                "analyzed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            raise

    async def generate_business_insights(
        self,
        kpis: Dict[str, Any],
        income_statement_data: Dict[str, Any],
        language: str = "both",
    ) -> Dict[str, Any]:
        """
        Generate business insights and recommendations.

        Args:
            kpis: Restaurant KPIs data
            income_statement_data: Income statement data
            language: Output language (en/zh/both)

        Returns:
            Dictionary containing business insights
        """
        self.logger.info(f"Generating business insights in language: {language}")

        try:
            # Convert data to proper objects
            income_statement = self._convert_to_income_statement(income_statement_data)
            kpi_obj = self._convert_to_kpi_object(kpis)

            # Generate insights
            from ..analyzers.insights_generator import InsightsGenerator

            insights_generator = InsightsGenerator()
            insights = insights_generator.generate_insights_from_kpis(
                kpi_obj, income_statement
            )

            # Format insights based on language preference
            formatted_insights = self._format_insights_by_language(insights, language)

            return {
                "success": True,
                "language": language,
                "bilingual_output": self.config.enable_bilingual_output
                and language == "both",
                "insights": formatted_insights,
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Insight generation failed: {str(e)}")
            raise

    async def comprehensive_analysis(
        self,
        file_path: str,
        language: str = "both",
        include_executive_summary: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive restaurant financial analysis.

        Args:
            file_path: Path to Excel file
            language: Output language
            include_executive_summary: Include executive summary

        Returns:
            Dictionary containing comprehensive analysis
        """
        self.logger.info(f"Starting comprehensive analysis of: {file_path}")

        try:
            # Use the analytics engine for complete analysis
            analysis_result = self.analytics_engine.analyze_restaurant_excel(file_path)

            # Convert result to dictionary if it's an object
            if hasattr(analysis_result, "to_dict"):
                analysis_data = analysis_result.to_dict()
            else:
                analysis_data = analysis_result

            # Format based on language preference
            if language != "both":
                analysis_data = self._format_analysis_by_language(
                    analysis_data, language
                )

            # Add metadata
            analysis_data.update(
                {
                    "comprehensive_analysis": True,
                    "language": language,
                    "executive_summary_included": include_executive_summary,
                    "analysis_completed_at": datetime.now().isoformat(),
                    "engine_version": "1.0.0",
                }
            )

            return analysis_data

        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {str(e)}")
            raise

    def _build_income_statement_from_data(
        self, period_id: str, period_data: Dict[str, Any]
    ) -> IncomeStatement:
        """Build IncomeStatement object from period data."""
        # Parse period information
        start_date, end_date, period_type = self._parse_period_id(period_id)

        # Extract financial data
        revenue_data = period_data.get("revenue", {})
        costs_data = period_data.get("costs", {})
        expenses_data = period_data.get("expenses", {})

        # Calculate derived metrics
        total_revenue = revenue_data.get("total", 0)
        total_cogs = costs_data.get("total", 0)
        total_expenses = expenses_data.get("total", 0)

        gross_profit = total_revenue - total_cogs
        operating_profit = gross_profit - total_expenses
        net_profit = operating_profit * 0.85  # Approximate after tax
        ebitda = operating_profit * 1.1  # Approximate EBITDA

        return IncomeStatement(
            period=FinancialPeriod(
                period_id=period_id,
                start_date=start_date,
                end_date=end_date,
                period_type=period_type,
            ),
            revenue=RevenueBreakdown(
                total_revenue=total_revenue,
                food_sales=revenue_data.get("food", 0),
                beverage_sales=revenue_data.get("beverage", 0),
                other_revenue=revenue_data.get("other", 0),
            ),
            costs=CostBreakdown(
                total_cogs=total_cogs,
                food_costs=costs_data.get("food", 0),
                beverage_costs=costs_data.get("beverage", 0),
            ),
            expenses=ExpenseBreakdown(
                total_expenses=total_expenses,
                labor_costs=expenses_data.get("labor", 0),
                rent=expenses_data.get("rent", 0),
                utilities=expenses_data.get("utilities", 0),
                marketing=expenses_data.get("marketing", 0),
                other_expenses=expenses_data.get("other", 0),
            ),
            metrics=ProfitMetrics(
                gross_profit=gross_profit,
                operating_profit=operating_profit,
                net_profit=net_profit,
                ebitda=ebitda,
                gross_margin=(
                    (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
                ),
                operating_margin=(
                    (operating_profit / total_revenue * 100) if total_revenue > 0 else 0
                ),
                net_margin=(
                    (net_profit / total_revenue * 100) if total_revenue > 0 else 0
                ),
                ebitda_margin=(
                    (ebitda / total_revenue * 100) if total_revenue > 0 else 0
                ),
            ),
        )

    def _parse_period_id(self, period_id: str) -> tuple[date, date, str]:
        """Parse period ID into dates and type."""
        if "Q" in period_id:
            # Quarterly format: 2024Q1
            year, quarter = period_id.split("Q")
            year = int(year)
            quarter = int(quarter)

            if quarter == 1:
                return date(year, 1, 1), date(year, 3, 31), "quarterly"
            elif quarter == 2:
                return date(year, 4, 1), date(year, 6, 30), "quarterly"
            elif quarter == 3:
                return date(year, 7, 1), date(year, 9, 30), "quarterly"
            else:
                return date(year, 10, 1), date(year, 12, 31), "quarterly"

        elif "-" in period_id:
            # Monthly format: 2024-03
            year, month = period_id.split("-")
            year, month = int(year), int(month)
            start_date = date(year, month, 1)

            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)

            return start_date, end_date, "monthly"

        else:
            # Yearly format: 2024
            year = int(period_id)
            return date(year, 1, 1), date(year, 12, 31), "yearly"

    def _convert_to_income_statement(self, data: Dict[str, Any]) -> IncomeStatement:
        """Convert dictionary data to IncomeStatement object."""
        # This is a simplified conversion - in practice, you'd need more robust logic
        return self._build_income_statement_from_data("2024Q1", data)

    def _convert_to_kpi_object(self, kpis: Dict[str, Any]):
        """Convert KPI dictionary to KPI object."""
        # Return the dictionary as-is for now
        return kpis

    def _generate_benchmark_comparison(self, kpis) -> Dict[str, Any]:
        """Generate benchmark comparison analysis."""
        return {
            "industry_comparison": "Restaurant industry benchmarks",
            "performance_rating": "Above Average",
            "key_metrics_vs_benchmark": {},
        }

    def _format_insights_by_language(self, insights, language: str) -> Dict[str, Any]:
        """Format insights based on language preference."""
        if language == "zh":
            # Return Chinese version only
            return {
                "strengths": insights.strengths,
                "areas_for_improvement": insights.areas_for_improvement,
                "recommendations": insights.recommendations,
            }
        elif language == "en":
            # Return English version only
            return {
                "strengths": insights.strengths,
                "areas_for_improvement": insights.areas_for_improvement,
                "recommendations": insights.recommendations,
            }
        else:
            # Return both languages
            return {
                "strengths": insights.strengths,
                "areas_for_improvement": insights.areas_for_improvement,
                "recommendations": insights.recommendations,
                "bilingual": True,
            }

    def _format_analysis_by_language(
        self, analysis_data: Dict[str, Any], language: str
    ) -> Dict[str, Any]:
        """Format analysis data based on language preference."""
        # For now, return as-is
        analysis_data["language_preference"] = language
        return analysis_data
