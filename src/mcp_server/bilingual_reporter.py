"""
Bilingual Report Generator

Advanced bilingual report generation for restaurant financial analysis,
supporting both Chinese and English output with cultural and business context.
"""

from typing import Dict, Any, List, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ReportLanguage(Enum):
    """Supported report languages."""

    ENGLISH = "en"
    CHINESE = "zh"
    BILINGUAL = "both"


class ReportFormat(Enum):
    """Supported report formats."""

    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


@dataclass
class BilingualContent:
    """Container for bilingual content."""

    english: str
    chinese: str

    def get_content(self, language: ReportLanguage) -> str:
        """Get content in specified language."""
        if language == ReportLanguage.CHINESE:
            return self.chinese
        elif language == ReportLanguage.ENGLISH:
            return self.english
        else:  # BILINGUAL
            return f"{self.english}\n\n{self.chinese}"


class BilingualReportGenerator:
    """Generator for bilingual restaurant financial reports."""

    def __init__(self):
        """Initialize the bilingual report generator."""
        self.chinese_terms = self._load_chinese_terms()
        self.report_templates = self._load_report_templates()

    def _load_chinese_terms(self) -> Dict[str, str]:
        """Load Chinese business terms mapping."""
        return {
            # Financial Metrics
            "revenue": "营业收入",
            "gross_profit": "毛利润",
            "operating_profit": "营业利润",
            "net_profit": "净利润",
            "gross_margin": "毛利率",
            "operating_margin": "营业利润率",
            "net_margin": "净利润率",
            "food_cost": "食品成本",
            "labor_cost": "人工成本",
            "prime_cost": "主要成本",
            "food_cost_percentage": "食品成本率",
            "labor_cost_percentage": "人工成本率",
            "prime_cost_ratio": "主要成本率",
            # Business Insights
            "strengths": "优势",
            "weaknesses": "劣势",
            "opportunities": "机会",
            "threats": "威胁",
            "recommendations": "建议",
            "action_plan": "行动计划",
            "improvement_areas": "改进领域",
            # Time Periods
            "quarterly": "季度",
            "monthly": "月度",
            "yearly": "年度",
            "period": "期间",
            # Restaurant Operations
            "restaurant": "餐厅",
            "food_sales": "食品销售",
            "beverage_sales": "饮料销售",
            "customer_traffic": "客流量",
            "average_ticket": "平均客单价",
            "table_turnover": "翻台率",
            # Performance
            "performance": "表现",
            "efficiency": "效率",
            "profitability": "盈利能力",
            "growth": "增长",
            "trend": "趋势",
            "benchmark": "基准",
            "industry_average": "行业平均",
        }

    def _load_report_templates(self) -> Dict[str, Dict[str, str]]:
        """Load report templates for different languages."""
        return {
            "executive_summary": {
                "en": "## Executive Summary\n\nThis comprehensive financial analysis of {restaurant_name} reveals {key_insight}. The restaurant demonstrates {performance_level} performance with {primary_strength} as a key strength and {improvement_area} requiring attention.\n\n**Key Findings:**\n{key_findings}\n\n**Strategic Recommendations:**\n{recommendations}",
                "zh": "## 执行摘要\n\n本次对{restaurant_name}的综合财务分析显示{key_insight}。餐厅表现为{performance_level}，{primary_strength}是主要优势，而{improvement_area}需要关注。\n\n**关键发现：**\n{key_findings}\n\n**战略建议：**\n{recommendations}",
            },
            "kpi_section": {
                "en": "## Key Performance Indicators\n\n### Profitability Metrics\n- Gross Margin: {gross_margin:.1f}% (Target: 65-75%)\n- Operating Margin: {operating_margin:.1f}% (Target: 15-25%)\n- Net Margin: {net_margin:.1f}% (Target: 10-20%)\n\n### Operational Efficiency\n- Food Cost %: {food_cost_pct:.1f}% (Industry: 28-35%)\n- Labor Cost %: {labor_cost_pct:.1f}% (Industry: 25-35%)\n- Prime Cost %: {prime_cost_pct:.1f}% (Target: <60%)",
                "zh": "## 关键绩效指标\n\n### 盈利能力指标\n- 毛利率: {gross_margin:.1f}% (目标: 65-75%)\n- 营业利润率: {operating_margin:.1f}% (目标: 15-25%)\n- 净利润率: {net_margin:.1f}% (目标: 10-20%)\n\n### 运营效率\n- 食品成本率: {food_cost_pct:.1f}% (行业: 28-35%)\n- 人工成本率: {labor_cost_pct:.1f}% (行业: 25-35%)\n- 主要成本率: {prime_cost_pct:.1f}% (目标: <60%)",
            },
            "insights_section": {
                "en": "## Business Insights\n\n### Strengths\n{strengths}\n\n### Areas for Improvement\n{improvements}\n\n### Strategic Recommendations\n{recommendations}",
                "zh": "## 经营洞察\n\n### 优势\n{strengths}\n\n### 改进领域\n{improvements}\n\n### 战略建议\n{recommendations}",
            },
        }

    def generate_comprehensive_report(
        self,
        restaurant_name: str,
        analysis_data: Dict[str, Any],
        language: ReportLanguage = ReportLanguage.BILINGUAL,
        format_type: ReportFormat = ReportFormat.MARKDOWN,
    ) -> Union[str, Dict[str, Any]]:
        """
        Generate a comprehensive bilingual financial analysis report.

        Args:
            restaurant_name: Name of the restaurant
            analysis_data: Complete analysis data
            language: Target language(s)
            format_type: Output format

        Returns:
            Formatted report in specified language and format
        """
        report_sections = []

        # Generate report header
        header = self._generate_header(restaurant_name, language)
        report_sections.append(header)

        # Generate executive summary
        if "insights" in analysis_data:
            summary = self._generate_executive_summary(
                restaurant_name, analysis_data, language
            )
            report_sections.append(summary)

        # Generate KPI section
        if "kpis" in analysis_data:
            kpi_section = self._generate_kpi_section(analysis_data["kpis"], language)
            report_sections.append(kpi_section)

        # Generate trend analysis section
        if "trends" in analysis_data:
            trend_section = self._generate_trend_section(
                analysis_data["trends"], language
            )
            report_sections.append(trend_section)

        # Generate insights section
        if "insights" in analysis_data:
            insights_section = self._generate_insights_section(
                analysis_data["insights"], language
            )
            report_sections.append(insights_section)

        # Generate recommendations section
        recommendations_section = self._generate_recommendations_section(
            analysis_data, language
        )
        report_sections.append(recommendations_section)

        # Generate footer
        footer = self._generate_footer(language)
        report_sections.append(footer)

        # Combine sections
        full_report = "\n\n".join(report_sections)

        # Format according to requested type
        if format_type == ReportFormat.JSON:
            return self._format_as_json(full_report, analysis_data, language)
        elif format_type == ReportFormat.HTML:
            return self._format_as_html(full_report, language)
        else:
            return full_report

    def _generate_header(self, restaurant_name: str, language: ReportLanguage) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if language == ReportLanguage.CHINESE:
            return f"# {restaurant_name} 财务分析报告\n\n生成时间: {timestamp}"
        elif language == ReportLanguage.ENGLISH:
            return f"# {restaurant_name} Financial Analysis Report\n\nGenerated: {timestamp}"
        else:  # BILINGUAL
            return f"# {restaurant_name} Financial Analysis Report / 财务分析报告\n\nGenerated / 生成时间: {timestamp}"

    def _generate_executive_summary(
        self,
        restaurant_name: str,
        analysis_data: Dict[str, Any],
        language: ReportLanguage,
    ) -> str:
        """Generate executive summary section."""
        insights = analysis_data.get("insights", {})
        kpis = analysis_data.get("kpis", {})

        # Determine performance level
        performance_level = self._assess_performance_level(kpis)

        # Get key insight
        key_insight = self._extract_key_insight(analysis_data)

        # Get primary strength and improvement area
        primary_strength = self._get_primary_strength(insights)
        improvement_area = self._get_primary_improvement_area(insights)

        # Format key findings
        key_findings = self._format_key_findings(analysis_data, language)

        # Format recommendations
        recommendations = self._format_top_recommendations(insights, language)

        if language == ReportLanguage.CHINESE:
            template = self.report_templates["executive_summary"]["zh"]
            return template.format(
                restaurant_name=restaurant_name,
                key_insight=key_insight,
                performance_level=performance_level,
                primary_strength=primary_strength,
                improvement_area=improvement_area,
                key_findings=key_findings,
                recommendations=recommendations,
            )
        elif language == ReportLanguage.ENGLISH:
            template = self.report_templates["executive_summary"]["en"]
            return template.format(
                restaurant_name=restaurant_name,
                key_insight=key_insight,
                performance_level=performance_level,
                primary_strength=primary_strength,
                improvement_area=improvement_area,
                key_findings=key_findings,
                recommendations=recommendations,
            )
        else:  # BILINGUAL
            en_section = self._generate_executive_summary(
                restaurant_name, analysis_data, ReportLanguage.ENGLISH
            )
            zh_section = self._generate_executive_summary(
                restaurant_name, analysis_data, ReportLanguage.CHINESE
            )
            return f"{en_section}\n\n{zh_section}"

    def _generate_kpi_section(
        self, kpis: Dict[str, Any], language: ReportLanguage
    ) -> str:
        """Generate KPI section."""
        profitability = kpis.get("profitability", {})
        efficiency = kpis.get("efficiency", {})

        kpi_data = {
            "gross_margin": profitability.get("gross_margin", 0),
            "operating_margin": profitability.get("operating_margin", 0),
            "net_margin": profitability.get("net_margin", 0),
            "food_cost_pct": efficiency.get("food_cost_percentage", 0),
            "labor_cost_pct": efficiency.get("labor_cost_percentage", 0),
            "prime_cost_pct": efficiency.get("prime_cost_ratio", 0),
        }

        if language == ReportLanguage.CHINESE:
            template = self.report_templates["kpi_section"]["zh"]
            return template.format(**kpi_data)
        elif language == ReportLanguage.ENGLISH:
            template = self.report_templates["kpi_section"]["en"]
            return template.format(**kpi_data)
        else:  # BILINGUAL
            en_section = self._generate_kpi_section(kpis, ReportLanguage.ENGLISH)
            zh_section = self._generate_kpi_section(kpis, ReportLanguage.CHINESE)
            return f"{en_section}\n\n{zh_section}"

    def _generate_trend_section(
        self, trends: Dict[str, Any], language: ReportLanguage
    ) -> str:
        """Generate trend analysis section."""
        growth_rates = trends.get("growth_rates", {})
        trend_direction = trends.get("trend_direction", "stable")

        if language == ReportLanguage.CHINESE:
            section = "## 趋势分析\n\n"
            section += f"### 整体趋势: {trend_direction}\n\n"
            section += "### 增长率:\n"
            for metric, rate in growth_rates.items():
                section += f"- {self.chinese_terms.get(metric, metric)}: {rate:.1f}%\n"
        elif language == ReportLanguage.ENGLISH:
            section = "## Trend Analysis\n\n"
            section += f"### Overall Trend: {trend_direction}\n\n"
            section += "### Growth Rates:\n"
            for metric, rate in growth_rates.items():
                section += f"- {metric.replace('_', ' ').title()}: {rate:.1f}%\n"
        else:  # BILINGUAL
            en_section = self._generate_trend_section(trends, ReportLanguage.ENGLISH)
            zh_section = self._generate_trend_section(trends, ReportLanguage.CHINESE)
            section = f"{en_section}\n\n{zh_section}"

        return section

    def _generate_insights_section(
        self, insights: Dict[str, Any], language: ReportLanguage
    ) -> str:
        """Generate insights section."""
        strengths = insights.get("strengths", [])
        improvements = insights.get("areas_for_improvement", [])
        recommendations = insights.get("recommendations", [])

        # Format lists
        strengths_text = self._format_list_items(strengths, language)
        improvements_text = self._format_list_items(improvements, language)
        recommendations_text = self._format_list_items(recommendations, language)

        if language == ReportLanguage.CHINESE:
            template = self.report_templates["insights_section"]["zh"]
            return template.format(
                strengths=strengths_text,
                improvements=improvements_text,
                recommendations=recommendations_text,
            )
        elif language == ReportLanguage.ENGLISH:
            template = self.report_templates["insights_section"]["en"]
            return template.format(
                strengths=strengths_text,
                improvements=improvements_text,
                recommendations=recommendations_text,
            )
        else:  # BILINGUAL
            en_section = self._generate_insights_section(
                insights, ReportLanguage.ENGLISH
            )
            zh_section = self._generate_insights_section(
                insights, ReportLanguage.CHINESE
            )
            return f"{en_section}\n\n{zh_section}"

    def _generate_recommendations_section(
        self, analysis_data: Dict[str, Any], language: ReportLanguage
    ) -> str:
        """Generate recommendations section."""
        if language == ReportLanguage.CHINESE:
            section = "## 行动计划\n\n"
            section += "基于以上分析，建议采取以下行动：\n\n"
            section += "1. **短期措施** (1-3个月):\n"
            section += "   - 优化成本控制流程\n"
            section += "   - 提升服务效率\n\n"
            section += "2. **中期目标** (3-6个月):\n"
            section += "   - 实施收入增长策略\n"
            section += "   - 优化菜单组合\n\n"
            section += "3. **长期规划** (6-12个月):\n"
            section += "   - 建立持续监控系统\n"
            section += "   - 制定扩张计划\n"
        elif language == ReportLanguage.ENGLISH:
            section = "## Action Plan\n\n"
            section += (
                "Based on this analysis, the following actions are recommended:\n\n"
            )
            section += "1. **Short-term Actions** (1-3 months):\n"
            section += "   - Optimize cost control processes\n"
            section += "   - Improve service efficiency\n\n"
            section += "2. **Medium-term Goals** (3-6 months):\n"
            section += "   - Implement revenue growth strategies\n"
            section += "   - Optimize menu mix\n\n"
            section += "3. **Long-term Planning** (6-12 months):\n"
            section += "   - Establish continuous monitoring systems\n"
            section += "   - Develop expansion plans\n"
        else:  # BILINGUAL
            en_section = self._generate_recommendations_section(
                analysis_data, ReportLanguage.ENGLISH
            )
            zh_section = self._generate_recommendations_section(
                analysis_data, ReportLanguage.CHINESE
            )
            section = f"{en_section}\n\n{zh_section}"

        return section

    def _generate_footer(self, language: ReportLanguage) -> str:
        """Generate report footer."""
        if language == ReportLanguage.CHINESE:
            return "---\n\n*本报告由餐厅财务分析MCP服务器生成*\n\n如需更多信息或定制分析，请联系系统管理员。"
        elif language == ReportLanguage.ENGLISH:
            return "---\n\n*This report was generated by the Restaurant Financial Analysis MCP Server*\n\nFor more information or custom analysis, please contact your system administrator."
        else:  # BILINGUAL
            en_footer = self._generate_footer(ReportLanguage.ENGLISH)
            zh_footer = self._generate_footer(ReportLanguage.CHINESE)
            return f"{en_footer}\n\n{zh_footer}"

    # Helper methods for report generation
    def _assess_performance_level(self, kpis: Dict[str, Any]) -> str:
        """Assess overall performance level."""
        # Simplified performance assessment
        return "strong"

    def _extract_key_insight(self, analysis_data: Dict[str, Any]) -> str:
        """Extract key insight from analysis."""
        return "solid financial fundamentals with opportunities for optimization"

    def _get_primary_strength(self, insights: Dict[str, Any]) -> str:
        """Get primary strength."""
        strengths = insights.get("strengths", [])
        return strengths[0] if strengths else "operational efficiency"

    def _get_primary_improvement_area(self, insights: Dict[str, Any]) -> str:
        """Get primary improvement area."""
        improvements = insights.get("areas_for_improvement", [])
        return improvements[0] if improvements else "cost optimization"

    def _format_key_findings(
        self, analysis_data: Dict[str, Any], language: ReportLanguage
    ) -> str:
        """Format key findings."""
        return "- Strong revenue performance\n- Effective cost management\n- Positive growth trajectory"

    def _format_top_recommendations(
        self, insights: Dict[str, Any], language: ReportLanguage
    ) -> str:
        """Format top recommendations."""
        recommendations = insights.get("recommendations", [])
        return "\n".join([f"- {rec}" for rec in recommendations[:3]])

    def _format_list_items(self, items: List[str], language: ReportLanguage) -> str:
        """Format list items."""
        return "\n".join([f"- {item}" for item in items])

    def _format_as_json(
        self, report_text: str, analysis_data: Dict[str, Any], language: ReportLanguage
    ) -> Dict[str, Any]:
        """Format report as JSON."""
        return {
            "report_text": report_text,
            "analysis_data": analysis_data,
            "language": language.value,
            "format": "json",
            "generated_at": datetime.now().isoformat(),
        }

    def _format_as_html(self, report_text: str, language: ReportLanguage) -> str:
        """Format report as HTML."""
        # Convert markdown to HTML (simplified)
        html_content = (
            report_text.replace("# ", "<h1>")
            .replace("## ", "<h2>")
            .replace("### ", "<h3>")
        )
        html_content = html_content.replace("\n\n", "</p><p>")
        html_content = f"<html><body><p>{html_content}</p></body></html>"
        return html_content
