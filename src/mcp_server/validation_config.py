"""
Validation-focused tool description overrides for financial analysis.

Following Serena's pattern of using tool description overrides to inject
validation requirements without modifying tool code.
"""

# Tool description overrides that enforce validation workflow
VALIDATION_TOOL_DESCRIPTIONS = {
    "parse_excel": """
CRITICAL: This tool only extracts raw data structure. Before using output for calculations:

1. MUST show account hierarchy to user for confirmation
2. MUST identify parent vs child accounts to prevent double counting
3. MUST confirm depreciation/amortization periods
4. NEVER proceed to calculations without user validation

Parse Chinese restaurant Excel files and extract account structure.
Returns: File structure, account hierarchy, validation warnings.

WORKFLOW ENFORCEMENT:
- Always follow with validation confirmation
- Present account tree to user before any analysis
- Document all assumptions in final reports
""",
    "calculate_kpis": """
VALIDATION REQUIRED: This tool requires pre-validated account structure.

Before calling this tool:
1. MUST have confirmed account hierarchy from parse_excel
2. MUST have user-confirmed depreciation periods
3. MUST use only leaf accounts (not parent summaries)
4. MUST document all assumptions used

Calculate restaurant KPIs and performance metrics from VALIDATED financial data.
Only proceeds with user-confirmed account mappings and assumptions.
""",
    "comprehensive_analysis": """
COMPREHENSIVE VALIDATION WORKFLOW:

This tool performs complete analysis but REQUIRES validation checkpoints:

MANDATORY STEPS:
1. Parse Excel and show account structure to user
2. Ask: "Is this account hierarchy correct?"
3. Confirm: "What depreciation periods apply?"
4. Ask: "What benchmarks should we use?"
5. Document all assumptions in report

DO NOT generate analysis without completing validation workflow.
Results must show validation steps performed.
""",
    "adaptive_financial_analysis": """
INTELLIGENT VALIDATION WORKFLOW:

This tool adapts to any Excel format but MUST validate before analysis:

VALIDATION PROTOCOL:
1. Parse file structure intelligently
2. Present discovered account hierarchy
3. Interactive user confirmation of:
   - Account parent-child relationships
   - Depreciation/amortization assumptions
   - Business context factors
   - Benchmark preferences
4. Document validation decisions

Only proceed with calculations after user confirms all assumptions.
Show validation audit trail in results.
""",
}

# Context-specific validation prompts
VALIDATION_PROMPTS = {
    "financial_analysis_context": """
You are a financial analysis agent with MANDATORY validation protocols.

CORE PRINCIPLE: Never calculate without validation.

WORKFLOW REQUIREMENTS:
1. Always parse Excel structure first
2. Present account hierarchy to user for confirmation
3. Ask about assumptions (depreciation periods, benchmarks)
4. Get explicit user approval before calculations
5. Document validation steps in all reports

VALIDATION CHECKPOINTS:
- "Is this account structure correct?"
- "What depreciation periods apply?"
- "Which accounts should be used for calculations?"
- "What benchmarks do you prefer?"

NEVER skip validation steps. NEVER assume user preferences.
""",
    "investment_analysis_context": """
Investment analysis requires CRITICAL validation of:

1. TOTAL INVESTMENT CALCULATION:
   - Confirm depreciation periods before back-calculating
   - Verify parent vs child account usage
   - Check for double counting

2. BENCHMARK ASSUMPTIONS:
   - Ask user about expected returns
   - Confirm risk tolerances
   - Validate market comparisons

3. PAYBACK CALCULATIONS:
   - Confirm revenue assumptions
   - Validate cost projections
   - Document sensitivity factors

Present ALL assumptions before generating investment recommendations.
""",
}
