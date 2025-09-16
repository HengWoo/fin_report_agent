"""
Phase 2 Demonstration: Data Validation and Quality Scoring

This script demonstrates the advanced validation and data quality features
implemented in Phase 2 of the Financial Reporting Agent.
"""

from decimal import Decimal
from src.transformers.data_transformer import DataTransformer, analyze_restaurant_excel
from src.models.financial_data import *
from src.validators.restaurant_validator import ValidationEngine
import json


def demo_validation_system():
    """Demonstrate the complete validation system."""
    print("=" * 70)
    print("🏪 FINANCIAL REPORTING AGENT - PHASE 2 DEMONSTRATION")
    print("=" * 70)
    print()

    # Demo 1: Excel File Analysis
    print("📊 DEMO 1: Complete Excel Analysis Pipeline")
    print("-" * 50)

    file_path = "data/sample_restaurant_income_2025.xlsx"
    result = analyze_restaurant_excel(file_path)

    if result.success:
        print(f"✅ Successfully processed: {file_path}")
        print(f"📈 Data Quality Score: {result.quality_score.overall_score:.1%}")
        print(f"⚠️  Validation Issues: {len(result.validation_result.issues)}")

        income_statement = result.income_statement
        print(f"\n💰 Financial Summary:")
        print(f"   Revenue: ¥{income_statement.revenue.total_revenue:,.0f}")
        print(f"   Gross Profit: ¥{income_statement.metrics.gross_profit:,.0f}")
        print(f"   Gross Margin: {income_statement.metrics.gross_margin:.1%}")

        if income_statement.metrics.food_cost_ratio:
            print(f"   Food Cost Ratio: {income_statement.metrics.food_cost_ratio:.1%}")
        if income_statement.metrics.labor_cost_ratio:
            print(f"   Labor Cost Ratio: {income_statement.metrics.labor_cost_ratio:.1%}")

        # Show validation issues
        if result.validation_result.issues:
            print(f"\n⚠️  Validation Issues Found:")
            for issue in result.validation_result.issues[:3]:  # Show first 3
                print(f"   {issue.severity.upper()}: {issue.message}")
        else:
            print("\n✅ No validation issues found!")

    else:
        print(f"❌ Failed to process file: {'; '.join(result.errors)}")

    print()

    # Demo 2: Create Sample Restaurants for Validation Testing
    print("🧪 DEMO 2: Restaurant Validation Scenarios")
    print("-" * 50)

    scenarios = [
        ("Healthy Restaurant", create_healthy_restaurant()),
        ("Struggling Restaurant", create_struggling_restaurant()),
        ("High-Cost Restaurant", create_high_cost_restaurant())
    ]

    validation_engine = ValidationEngine()

    for name, restaurant in scenarios:
        print(f"\n🏪 {name}:")
        validation_result, quality_score = validation_engine.validate_with_quality_score(restaurant)

        print(f"   Quality Score: {quality_score.overall_score:.1%}")
        print(f"   Valid: {'✅' if validation_result.is_valid else '❌'}")
        print(f"   Issues: {len(validation_result.issues)} ({validation_result.errors_count} errors, {validation_result.warnings_count} warnings)")

        # Show key metrics
        metrics = restaurant.metrics
        print(f"   Gross Margin: {metrics.gross_margin:.1%}")
        if metrics.food_cost_ratio:
            print(f"   Food Cost: {metrics.food_cost_ratio:.1%}")
        if metrics.prime_cost_ratio:
            print(f"   Prime Cost: {metrics.prime_cost_ratio:.1%}")

        # Show top issues
        if validation_result.issues:
            critical_issues = [i for i in validation_result.issues if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]
            if critical_issues:
                print(f"   🚨 Critical Issue: {critical_issues[0].message}")

    print()

    # Demo 3: Data Quality Breakdown
    print("📊 DEMO 3: Data Quality Analysis")
    print("-" * 50)

    if result.success and result.quality_score:
        quality = result.quality_score
        print(f"Overall Quality Score: {quality.overall_score:.1%}")
        print(f"├── Completeness: {quality.completeness_score:.1%}")
        print(f"├── Accuracy: {quality.accuracy_score:.1%}")
        print(f"└── Consistency: {quality.consistency_score:.1%}")
        print()
        print("Category Quality Scores:")
        print(f"├── Revenue Quality: {quality.revenue_quality:.1%}")
        print(f"├── Cost Quality: {quality.cost_quality:.1%}")
        print(f"└── Expense Quality: {quality.expense_quality:.1%}")

        if quality.missing_fields:
            print(f"\n📋 Missing Fields: {', '.join(quality.missing_fields)}")

        if quality.suspicious_values:
            print(f"\n🔍 Suspicious Values:")
            for value in quality.suspicious_values[:3]:
                print(f"   • {value}")

    print()

    # Demo 4: Industry Benchmarking
    print("📈 DEMO 4: Industry Benchmark Comparison")
    print("-" * 50)

    if result.success:
        metrics = result.income_statement.metrics

        benchmarks = {
            "Gross Margin": {
                "value": metrics.gross_margin,
                "healthy_range": (0.55, 0.75),
                "format": ".1%"
            },
            "Food Cost Ratio": {
                "value": metrics.food_cost_ratio,
                "healthy_range": (0.25, 0.35),
                "format": ".1%"
            },
            "Labor Cost Ratio": {
                "value": metrics.labor_cost_ratio,
                "healthy_range": (0.20, 0.30),
                "format": ".1%"
            },
            "Prime Cost Ratio": {
                "value": metrics.prime_cost_ratio,
                "healthy_range": (0.50, 0.65),
                "format": ".1%"
            }
        }

        for name, data in benchmarks.items():
            if data["value"] is not None:
                value = data["value"]
                min_healthy, max_healthy = data["healthy_range"]

                if min_healthy <= value <= max_healthy:
                    status = "✅ Healthy"
                elif value < min_healthy:
                    status = "⚠️  Below Range"
                else:
                    status = "🚨 Above Range"

                value_str = f"{value:{data['format']}}"
                range_str = f"{min_healthy:{data['format']}}-{max_healthy:{data['format']}}"
                print(f"{name:18}: {value_str:>7} {status:>12} (Healthy: {range_str})")

    print("\n" + "=" * 70)
    print("Phase 2 demonstration complete! 🎉")
    print("Key features showcased:")
    print("• Comprehensive data validation with restaurant-specific rules")
    print("• Multi-dimensional data quality scoring")
    print("• Industry benchmark comparisons")
    print("• Detailed error reporting and suggestions")
    print("• End-to-end Excel processing pipeline")
    print("=" * 70)


def create_healthy_restaurant():
    """Create a financially healthy restaurant example."""
    period = FinancialPeriod(period_id="2025-01", period_type=PeriodType.MONTHLY)

    revenue = RevenueBreakdown(
        total_revenue=Decimal('120000'),
        food_revenue=Decimal('95000'),
        beverage_revenue=Decimal('20000'),
        dessert_revenue=Decimal('5000')
    )

    costs = CostBreakdown(
        total_cogs=Decimal('42000'),
        food_cost=Decimal('28500'),  # 30% of food revenue
        beverage_cost=Decimal('8000'),
        dessert_cost=Decimal('2000'),
        other_cost=Decimal('3500')
    )

    expenses = ExpenseBreakdown(
        total_operating_expenses=Decimal('45000'),
        labor_cost=Decimal('30000'),  # 25% of revenue
        rent_expense=Decimal('12000'),
        utilities=Decimal('3000')
    )

    metrics = ProfitMetrics(
        gross_profit=Decimal('78000'),
        gross_margin=Decimal('0.65'),  # Healthy 65%
        operating_profit=Decimal('33000'),
        operating_margin=Decimal('0.275'),
        food_cost_ratio=Decimal('0.30'),  # Healthy 30%
        labor_cost_ratio=Decimal('0.25'),  # Healthy 25%
        prime_cost_ratio=Decimal('0.60')   # Healthy 60%
    )

    return IncomeStatement(
        period=period,
        revenue=revenue,
        costs=costs,
        expenses=expenses,
        metrics=metrics,
        restaurant_name="Golden Dragon Restaurant"
    )


def create_struggling_restaurant():
    """Create a struggling restaurant with multiple issues."""
    period = FinancialPeriod(period_id="2025-01", period_type=PeriodType.MONTHLY)

    revenue = RevenueBreakdown(
        total_revenue=Decimal('100000'),
        food_revenue=Decimal('85000'),
        beverage_revenue=Decimal('15000')
    )

    costs = CostBreakdown(
        total_cogs=Decimal('55000'),
        food_cost=Decimal('42500'),  # 50% - way too high!
        beverage_cost=Decimal('9000'),
        other_cost=Decimal('3500')
    )

    expenses = ExpenseBreakdown(
        total_operating_expenses=Decimal('38000'),
        labor_cost=Decimal('38000'),  # 38% - too high!
        rent_expense=Decimal('15000'),
        utilities=Decimal('5000')
    )

    metrics = ProfitMetrics(
        gross_profit=Decimal('45000'),
        gross_margin=Decimal('0.45'),  # Low margin
        operating_profit=Decimal('7000'),
        operating_margin=Decimal('0.07'),
        food_cost_ratio=Decimal('0.50'),  # Too high
        labor_cost_ratio=Decimal('0.38'),  # Too high
        prime_cost_ratio=Decimal('0.93')   # Critically high!
    )

    return IncomeStatement(
        period=period,
        revenue=revenue,
        costs=costs,
        expenses=expenses,
        metrics=metrics,
        restaurant_name="Struggling Noodle House"
    )


def create_high_cost_restaurant():
    """Create a restaurant with high costs but still viable."""
    period = FinancialPeriod(period_id="2025-01", period_type=PeriodType.MONTHLY)

    revenue = RevenueBreakdown(
        total_revenue=Decimal('150000'),
        food_revenue=Decimal('120000'),
        beverage_revenue=Decimal('25000'),
        dessert_revenue=Decimal('5000')
    )

    costs = CostBreakdown(
        total_cogs=Decimal('60000'),
        food_cost=Decimal('48000'),  # 40% - high but manageable for premium
        beverage_cost=Decimal('10000'),
        dessert_cost=Decimal('2000')
    )

    expenses = ExpenseBreakdown(
        total_operating_expenses=Decimal('55000'),
        labor_cost=Decimal('45000'),  # 30% - at upper limit
        rent_expense=Decimal('20000'),  # High rent location
        utilities=Decimal('5000')
    )

    metrics = ProfitMetrics(
        gross_profit=Decimal('90000'),
        gross_margin=Decimal('0.60'),  # Still decent
        operating_profit=Decimal('35000'),
        operating_margin=Decimal('0.233'),
        food_cost_ratio=Decimal('0.40'),  # High but acceptable for premium
        labor_cost_ratio=Decimal('0.30'),  # At limit
        prime_cost_ratio=Decimal('0.70')   # High but viable
    )

    return IncomeStatement(
        period=period,
        revenue=revenue,
        costs=costs,
        expenses=expenses,
        metrics=metrics,
        restaurant_name="Premium Dining House"
    )


if __name__ == "__main__":
    demo_validation_system()