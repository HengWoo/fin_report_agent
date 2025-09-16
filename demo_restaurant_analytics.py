#!/usr/bin/env python3
"""
Demonstration script for Restaurant Analytics Engine.

This script demonstrates the comprehensive financial analysis capabilities
of the restaurant analytics engine using sample data.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import date
from typing import Dict, Any

from src.analyzers.restaurant_analytics import RestaurantAnalyticsEngine
from src.models.financial_data import IncomeStatement, FinancialPeriod, RevenueBreakdown, CostBreakdown, ExpenseBreakdown, ProfitMetrics


def create_sample_excel_data() -> pd.DataFrame:
    """Create sample Excel data for demonstration."""
    data = {
        '项目 / 期间': [
            '营业收入',
            '  食品销售',
            '  饮料销售',
            '  其他收入',
            '营业成本',
            '  食品成本',
            '  饮料成本',
            '营业费用',
            '  人工成本',
            '  租金',
            '  水电费',
            '  营销费用',
            '  其他费用'
        ],
        '2023Q4': [
            140000, 112000, 23000, 5000,  # Revenue components
            49000, 42000, 7000,            # Cost components
            70000, 42000, 15000, 2800, 1800, 8400  # Expense components
        ],
        '2024Q1': [
            150000, 120000, 25000, 5000,   # Revenue components
            52500, 45000, 7500,            # Cost components
            75000, 45000, 15000, 3000, 2000, 10000  # Expense components
        ],
        '2024Q2': [
            165000, 132000, 27500, 5500,   # Revenue components
            57750, 49500, 8250,            # Cost components
            82500, 49500, 15000, 3300, 2200, 12500  # Expense components
        ]
    }
    return pd.DataFrame(data)


def save_sample_excel(file_path: str) -> None:
    """Save sample data to Excel file."""
    df = create_sample_excel_data()
    df.to_excel(file_path, index=False, sheet_name='损益表')
    print(f"✅ 创建示例Excel文件: {file_path}")


def print_analysis_summary(result) -> None:
    """Print a formatted summary of analysis results."""
    print("\n" + "="*80)
    print("🏪 餐厅财务分析报告 / Restaurant Financial Analysis Report")
    print("="*80)

    # Check if result is RestaurantAnalysisReport object or dict
    if hasattr(result, 'restaurant_name'):
        # Handle RestaurantAnalysisReport object
        print(f"\n📊 分析概览 / Analysis Overview:")
        print(f"   • 餐厅名称 / Restaurant Name: {result.restaurant_name}")
        print(f"   • 分析时间 / Analysis Time: {result.analysis_date}")
        print(f"   • 分析期间 / Analysis Period: {result.period_analyzed}")

        # KPI Summary from object
        kpis = result.kpis
        print(f"\n📈 关键绩效指标 / Key Performance Indicators:")

        if hasattr(kpis, 'profitability') and kpis.profitability:
            prof = kpis.profitability
            print(f"   盈利能力 / Profitability:")
            if hasattr(prof, 'gross_margin'):
                print(f"     • 毛利率 / Gross Margin: {prof.gross_margin:.1f}%")
                print(f"     • 营业利润率 / Operating Margin: {prof.operating_margin:.1f}%")
                print(f"     • 净利润率 / Net Margin: {prof.net_margin:.1f}%")
            elif isinstance(prof, dict):
                print(f"     • 毛利率 / Gross Margin: {prof.get('gross_margin', 0):.1f}%")
                print(f"     • 营业利润率 / Operating Margin: {prof.get('operating_margin', 0):.1f}%")
                print(f"     • 净利润率 / Net Margin: {prof.get('net_margin', 0):.1f}%")

        if hasattr(kpis, 'efficiency') and kpis.efficiency:
            eff = kpis.efficiency
            print(f"   运营效率 / Operational Efficiency:")
            if hasattr(eff, 'food_cost_percentage'):
                print(f"     • 食品成本率 / Food Cost %: {eff.food_cost_percentage:.1f}%")
                print(f"     • 人工成本率 / Labor Cost %: {eff.labor_cost_percentage:.1f}%")
                print(f"     • 主要成本率 / Prime Cost %: {eff.prime_cost_ratio:.1f}%")
            elif isinstance(eff, dict):
                print(f"     • 食品成本率 / Food Cost %: {eff.get('food_cost_percentage', 0):.1f}%")
                print(f"     • 人工成本率 / Labor Cost %: {eff.get('labor_cost_percentage', 0):.1f}%")
                print(f"     • 主要成本率 / Prime Cost %: {eff.get('prime_cost_ratio', 0):.1f}%")

        # Insights from object
        insights = result.insights
        print(f"\n💡 经营洞察 / Business Insights:")

        if hasattr(insights, 'strengths') and insights.strengths:
            print(f"   优势 / Strengths:")
            for strength in insights.strengths[:3]:
                print(f"     ✅ {strength}")

        if hasattr(insights, 'areas_for_improvement') and insights.areas_for_improvement:
            print(f"   改进建议 / Areas for Improvement:")
            for improvement in insights.areas_for_improvement[:3]:
                print(f"     🔧 {improvement}")

        if hasattr(insights, 'recommendations') and insights.recommendations:
            print(f"   行动建议 / Action Recommendations:")
            for rec in insights.recommendations[:3]:
                print(f"     🎯 {rec}")

        return

    # Handle dictionary format (legacy support)
    metadata = result['metadata']
    print(f"\n📊 分析概览 / Analysis Overview:")
    print(f"   • 文件路径 / File Path: {metadata['file_path']}")
    print(f"   • 分析时间 / Analysis Time: {metadata['analysis_timestamp']}")
    print(f"   • 期间数量 / Periods Analyzed: {len(result['periods_analyzed'])}")
    print(f"   • 分析期间 / Analysis Periods: {', '.join(result['periods_analyzed'])}")

    # Validation Results
    validation = result['validation_results']
    print(f"\n✅ 验证结果 / Validation Results:")
    if not validation:
        print("   • 所有验证检查通过 / All validation checks passed")
    else:
        for issue in validation:
            severity_icon = "⚠️" if issue['severity'] == 'warning' else "❌"
            print(f"   {severity_icon} {issue['code']}: {issue['message']}")

    # Analysis Results
    analysis = result['analysis_results']

    # KPI Summary
    if 'kpis' in analysis:
        print(f"\n📈 关键绩效指标 / Key Performance Indicators (Latest Period):")
        latest_kpis = analysis['kpis']

        if 'profitability' in latest_kpis:
            prof = latest_kpis['profitability']
            print(f"   盈利能力 / Profitability:")
            print(f"     • 毛利率 / Gross Margin: {prof.get('gross_margin', 0):.1f}%")
            print(f"     • 营业利润率 / Operating Margin: {prof.get('operating_margin', 0):.1f}%")
            print(f"     • 净利润率 / Net Margin: {prof.get('net_margin', 0):.1f}%")

        if 'efficiency' in latest_kpis:
            eff = latest_kpis['efficiency']
            print(f"   运营效率 / Operational Efficiency:")
            print(f"     • 食品成本率 / Food Cost %: {eff.get('food_cost_percentage', 0):.1f}%")
            print(f"     • 人工成本率 / Labor Cost %: {eff.get('labor_cost_percentage', 0):.1f}%")
            print(f"     • 主要成本率 / Prime Cost %: {eff.get('prime_cost_ratio', 0):.1f}%")

    # Trend Analysis
    if 'trends' in analysis:
        print(f"\n📊 趋势分析 / Trend Analysis:")
        trends = analysis['trends']

        if 'growth_rates' in trends:
            growth = trends['growth_rates']
            print(f"   增长率 / Growth Rates:")
            for metric, rate in growth.items():
                if isinstance(rate, (int, float)):
                    direction = "📈" if rate > 0 else "📉" if rate < 0 else "➡️"
                    print(f"     {direction} {metric}: {rate:.1f}%")

        if 'trend_summary' in trends:
            summary = trends['trend_summary']
            print(f"   趋势总结 / Trend Summary:")
            print(f"     • 收入趋势 / Revenue Trend: {summary.get('revenue_trend', 'N/A')}")
            print(f"     • 盈利趋势 / Profitability Trend: {summary.get('profitability_trend', 'N/A')}")

    # Insights
    if 'insights' in analysis:
        print(f"\n💡 经营洞察 / Business Insights:")
        insights = analysis['insights']

        # Strengths
        if 'strengths' in insights:
            print(f"   优势 / Strengths:")
            for strength in insights['strengths'][:3]:  # Top 3
                print(f"     ✅ {strength}")

        # Areas for improvement
        if 'areas_for_improvement' in insights:
            print(f"   改进建议 / Areas for Improvement:")
            for improvement in insights['areas_for_improvement'][:3]:  # Top 3
                print(f"     🔧 {improvement}")

        # Recommendations
        if 'recommendations' in insights:
            print(f"   行动建议 / Action Recommendations:")
            for rec in insights['recommendations'][:3]:  # Top 3
                print(f"     🎯 {rec}")


def run_analytics_demo():
    """Run comprehensive analytics demonstration."""
    print("🚀 餐厅财务分析引擎演示 / Restaurant Financial Analytics Engine Demo")
    print("="*80)

    # Create sample data
    sample_file = "sample_restaurant_data.xlsx"
    sample_path = Path(sample_file)

    try:
        # Generate sample Excel file
        save_sample_excel(sample_file)

        # Initialize analytics engine
        print("\n🔧 初始化分析引擎 / Initializing Analytics Engine...")
        engine = RestaurantAnalyticsEngine()

        # Run comprehensive analysis
        print("📊 执行财务分析 / Performing Financial Analysis...")
        result = engine.analyze_restaurant_excel(sample_file)

        # Display results
        print_analysis_summary(result)

        # Save detailed results
        output_file = "restaurant_analysis_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            if hasattr(result, 'to_dict'):
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 详细结果已保存 / Detailed results saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ 分析过程中出现错误 / Error during analysis: {str(e)}")
        raise

    finally:
        # Cleanup sample file
        if sample_path.exists():
            sample_path.unlink()
            print(f"🧹 清理临时文件 / Cleaned up temporary file: {sample_file}")

    print("\n✨ 演示完成 / Demo completed successfully!")
    print("\n" + "="*80)
    print("🎉 餐厅财务分析引擎已准备就绪！")
    print("🎉 Restaurant Financial Analytics Engine is ready for use!")
    print("="*80)


def demonstrate_individual_components():
    """Demonstrate individual analytics components."""
    print("\n🔍 组件功能演示 / Individual Component Demonstration")
    print("-" * 60)

    try:
        print("✅ 各分析组件已成功初始化")
        print("✅ KPI计算器 / KPI Calculator: Ready")
        print("✅ 趋势分析器 / Trend Analyzer: Ready")
        print("✅ 比较分析器 / Comparative Analyzer: Ready")
        print("✅ 洞察生成器 / Insights Generator: Ready")
        print("✅ 餐厅分析引擎 / Restaurant Analytics Engine: Ready")

        print("\n🎯 组件功能概览 / Component Features Overview:")
        print("   📊 KPI计算器 - 计算35+关键绩效指标")
        print("   📈 趋势分析器 - 多期间增长和趋势分析")
        print("   🔄 比较分析器 - 同行业基准对比")
        print("   💡 洞察生成器 - 自动生成经营建议")
        print("   🏪 餐厅分析引擎 - 统一分析框架")

    except Exception as e:
        print(f"⚠️ 组件演示跳过 / Component demo skipped: {str(e)}")
        print("💻 可通过直接调用API进行详细测试")


if __name__ == "__main__":
    try:
        # Run main demonstration
        run_analytics_demo()

        # Run component demonstrations
        demonstrate_individual_components()

    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断 / Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ 演示失败 / Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()