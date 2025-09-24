"""
Adaptive Financial Analyzer

Intelligent financial analysis that adapts to any Excel format using Claude Code agents.
No rigid schemas or predefined mappings - pure agent intelligence.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AdaptiveFinancialAnalyzer:
    """
    Intelligent financial analyzer that adapts to any Excel format.
    Uses Claude Code Task agents for flexible analysis.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def analyze_excel(
        self,
        file_path: str,
        analysis_focus: str = "comprehensive",
        business_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Intelligently analyze any financial Excel file.

        Args:
            file_path: Path to Excel file
            analysis_focus: "profitability", "growth", "efficiency", or "comprehensive"
            business_context: Optional context like "new_location", "seasonal_business"

        Returns:
            Comprehensive analysis results
        """
        try:
            # Quick validation
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Get file info for agent context
            file_info = self._get_file_info(file_path)

            # Create analysis prompt based on focus and context
            analysis_prompt = self._build_analysis_prompt(
                file_path, analysis_focus, business_context, file_info
            )

            # This will be filled in when we add the MCP tool integration
            # For now, return structured placeholder
            return {
                "status": "ready_for_agent_analysis",
                "file_path": file_path,
                "analysis_focus": analysis_focus,
                "business_context": business_context,
                "file_info": file_info,
                "analysis_prompt": analysis_prompt
            }

        except Exception as e:
            self.logger.error(f"Error in adaptive analysis: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "file_path": file_path
            }

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information to help agent understand context."""
        try:
            # Load Excel to understand structure
            xl_file = pd.ExcelFile(file_path)
            sheets = xl_file.sheet_names

            # Get first sheet info
            df = pd.read_excel(file_path, sheet_name=sheets[0])

            # Extract basic structure info
            info = {
                "filename": Path(file_path).name,
                "sheets": sheets,
                "shape": df.shape,
                "columns_sample": df.columns.tolist()[:10] if len(df.columns) > 0 else [],
                "first_row": df.iloc[0].tolist()[:10] if len(df) > 0 else [],
                "potential_headers": self._identify_potential_headers(df),
                "language_indicators": self._detect_language(df)
            }

            return info

        except Exception as e:
            return {
                "filename": Path(file_path).name,
                "error": str(e)
            }

    def _identify_potential_headers(self, df: pd.DataFrame) -> List[str]:
        """Identify rows that might contain headers."""
        potential_headers = []

        # Check first few rows for header-like content
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            # Look for month names, financial terms, etc.
            row_str = ' '.join([str(x) for x in row if pd.notna(x)])
            if any(term in row_str for term in ['月', '年', '收入', '成本', '费用', 'revenue', 'cost', 'profit']):
                potential_headers.append(f"Row {i}: {row_str[:100]}")

        return potential_headers

    def _detect_language(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect language and financial terminology used."""
        # Sample text from first column and first row
        text_sample = ""

        # Get first column text
        if len(df) > 0:
            first_col = df.iloc[:10, 0]
            text_sample += ' '.join([str(x) for x in first_col if pd.notna(x)])

        # Get first row text
        if len(df.columns) > 0:
            first_row = df.iloc[0] if len(df) > 0 else pd.Series()
            text_sample += ' '.join([str(x) for x in first_row if pd.notna(x)])

        chinese_indicators = ['收入', '成本', '费用', '利润', '营业', '月', '年']
        english_indicators = ['revenue', 'cost', 'profit', 'expense', 'operating']

        chinese_count = sum(1 for term in chinese_indicators if term in text_sample)
        english_count = sum(1 for term in english_indicators if term.lower() in text_sample.lower())

        return {
            "primary_language": "chinese" if chinese_count > english_count else "english",
            "chinese_terms_found": chinese_count,
            "english_terms_found": english_count,
            "sample_text": text_sample[:200]
        }

    def _build_analysis_prompt(
        self,
        file_path: str,
        analysis_focus: str,
        business_context: Optional[str],
        file_info: Dict[str, Any]
    ) -> str:
        """Build an intelligent prompt for the agent analysis."""

        prompt = f"""
You are analyzing the financial Excel file: {file_path}

FILE STRUCTURE CONTEXT:
- Filename: {file_info.get('filename', 'Unknown')}
- Sheets: {file_info.get('sheets', [])}
- Dimensions: {file_info.get('shape', 'Unknown')}
- Language: {file_info.get('language_indicators', {}).get('primary_language', 'Unknown')}
- Detected headers: {file_info.get('potential_headers', [])}

ANALYSIS FOCUS: {analysis_focus}
"""

        if business_context:
            prompt += f"BUSINESS CONTEXT: {business_context}\n"

        if analysis_focus == "profitability":
            prompt += """
PROFITABILITY ANALYSIS OBJECTIVES:
1. Find all revenue/income items (营业收入, 销售收入, 收入, revenue, sales, etc.)
2. Identify all cost categories (成本, 费用, cost, expense, etc.)
3. Calculate profit margins and efficiency ratios
4. Compare to industry standards where appropriate
5. Identify profitability trends and patterns
6. Generate specific recommendations for profit improvement

"""
        elif analysis_focus == "growth":
            prompt += """
GROWTH TREND ANALYSIS OBJECTIVES:
1. Identify time series data (months, quarters, years)
2. Calculate period-over-period growth rates
3. Analyze revenue growth patterns and seasonality
4. Identify growth drivers and constraints
5. Forecast future trends based on current patterns
6. Recommend strategies to sustain or accelerate growth

"""
        elif analysis_focus == "comprehensive":
            prompt += """
COMPREHENSIVE ANALYSIS OBJECTIVES:
1. REVENUE ANALYSIS: Find and analyze all income streams
2. COST ANALYSIS: Identify and categorize all expenses
3. PROFITABILITY: Calculate margins, ratios, and efficiency metrics
4. GROWTH TRENDS: Analyze period-over-period changes
5. OPERATIONAL INSIGHTS: Generate actionable business recommendations
6. BENCHMARK COMPARISON: Compare to industry standards where possible

"""

        prompt += """
ANALYSIS APPROACH:
- DO NOT assume any specific Excel format or structure
- Intelligently identify what each row and column represents
- Adapt your analysis to the actual data structure you find
- Handle missing data or irregular formats gracefully
- Generate insights based on what the data actually shows
- Provide bilingual analysis (Chinese/English) if the data appears to be Chinese

DELIVERABLES:
1. Executive Summary of key findings
2. Detailed financial metrics and calculations
3. Trend analysis with specific numbers
4. Business insights and recommendations
5. Clear explanation of methodology used

Be thorough, adaptive, and insightful in your analysis.
"""

        return prompt