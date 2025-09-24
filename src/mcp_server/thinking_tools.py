"""
Thinking and Reflection Tools for Multi-Turn Intelligence

This module provides metacognitive tools that enable Claude to reflect on
its analysis process, validate assumptions, and maintain analytical rigor.
Inspired by Serena's thinking tools for systematic reasoning.

Features:
- Financial data reflection
- Analysis completeness checking
- Assumption validation
- Insight capture and organization
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ThinkingResult:
    """Result of a thinking/reflection operation."""

    thought_type: str
    summary: str
    details: Dict[str, Any]
    recommendations: List[str]
    confidence: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thought_type": self.thought_type,
            "summary": self.summary,
            "details": self.details,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }


class FinancialThinkingTools:
    """Tools for metacognitive reflection on financial analysis."""

    def __init__(self):
        """Initialize thinking tools."""
        self.logger = logging.getLogger("thinking_tools")
        self.thought_history: List[ThinkingResult] = []

    def think_about_financial_data(
        self, collected_data: Dict[str, Any], analysis_goal: str
    ) -> ThinkingResult:
        """
        Reflect on collected financial data and its sufficiency.

        Like Serena's think_about_collected_information, this helps Claude
        determine if enough data has been gathered for the analysis goal.
        """
        details = {
            "data_sources": list(collected_data.keys()),
            "data_completeness": self._assess_completeness(collected_data),
            "analysis_goal": analysis_goal,
        }

        recommendations = []

        # Check data sufficiency
        if not collected_data:
            recommendations.append(
                "⚠️ No data collected yet. Start with get_excel_info or show_excel_visual"
            )
            confidence = 0.0
            summary = "No financial data collected"

        elif len(collected_data) < 3:
            recommendations.append(
                "Consider gathering more context with additional tools"
            )
            confidence = 0.5
            summary = "Minimal data collected, may need more context"

        else:
            # Check for key financial components
            has_revenue = any(
                "revenue" in str(k).lower() or "收入" in str(k)
                for k in collected_data.keys()
            )
            has_expenses = any(
                "expense" in str(k).lower() or "费用" in str(k) or "成本" in str(k)
                for k in collected_data.keys()
            )
            has_structure = any(
                "structure" in str(k).lower() or "hierarchy" in str(k).lower()
                for k in collected_data.keys()
            )

            if has_revenue and has_expenses and has_structure:
                confidence = 0.9
                summary = "Comprehensive data collected, ready for analysis"
                recommendations.append("✅ Data appears sufficient for analysis")
            else:
                confidence = 0.6
                summary = "Partial data collected"
                if not has_revenue:
                    recommendations.append("Consider searching for revenue/收入 data")
                if not has_expenses:
                    recommendations.append(
                        "Consider searching for expense/费用/成本 data"
                    )
                if not has_structure:
                    recommendations.append(
                        "Consider getting account structure/hierarchy"
                    )

        result = ThinkingResult(
            thought_type="data_reflection",
            summary=summary,
            details=details,
            recommendations=recommendations,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
        )

        self.thought_history.append(result)
        return result

    def think_about_analysis_completeness(
        self, analysis_performed: List[str], required_components: List[str]
    ) -> ThinkingResult:
        """
        Check if analysis is complete against requirements.

        Similar to Serena's completion checks, ensures all required
        analysis steps have been performed.
        """
        performed_set = set(c.lower() for c in analysis_performed)
        required_set = set(c.lower() for c in required_components)

        missing = required_set - performed_set
        completed = required_set & performed_set

        confidence = len(completed) / len(required_set) if required_set else 1.0

        details = {
            "completed_count": len(completed),
            "total_required": len(required_set),
            "completed": list(completed),
            "missing": list(missing),
            "completion_rate": f"{confidence * 100:.1f}%",
        }

        recommendations = []
        if missing:
            recommendations.append(
                f"⚠️ Missing analysis components: {', '.join(missing)}"
            )
            for component in missing:
                recommendations.append(f"  - Consider performing: {component}")
            summary = f"Analysis {confidence * 100:.0f}% complete - {len(missing)} components missing"
        else:
            recommendations.append("✅ All required analysis components completed")
            summary = "Analysis complete - all requirements met"

        result = ThinkingResult(
            thought_type="completeness_check",
            summary=summary,
            details=details,
            recommendations=recommendations,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
        )

        self.thought_history.append(result)
        return result

    def think_about_assumptions(
        self, assumptions: Dict[str, Any], financial_context: Dict[str, Any]
    ) -> ThinkingResult:
        """
        Validate financial assumptions against context and best practices.

        Ensures assumptions are reasonable and documented.
        """
        details = {
            "assumptions_count": len(assumptions),
            "assumptions": assumptions,
            "financial_context": financial_context,
        }

        recommendations = []
        validation_results = []

        for key, value in assumptions.items():
            validation = self._validate_assumption(key, value, financial_context)
            validation_results.append(validation)

            if not validation["valid"]:
                recommendations.append(f"⚠️ {key}: {validation['reason']}")

        valid_count = sum(1 for v in validation_results if v["valid"])
        confidence = valid_count / len(assumptions) if assumptions else 1.0

        details["validation_results"] = validation_results

        if confidence >= 0.8:
            summary = (
                f"Assumptions validated - {valid_count}/{len(assumptions)} acceptable"
            )
            if confidence == 1.0:
                recommendations.append("✅ All assumptions validated")
        else:
            summary = (
                f"Assumption concerns - only {valid_count}/{len(assumptions)} valid"
            )
            recommendations.insert(0, "⚠️ Review and confirm assumptions with user")

        result = ThinkingResult(
            thought_type="assumption_validation",
            summary=summary,
            details=details,
            recommendations=recommendations,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
        )

        self.thought_history.append(result)
        return result

    def think_about_next_steps(
        self, current_state: Dict[str, Any], goal: str
    ) -> ThinkingResult:
        """
        Determine optimal next steps in analysis workflow.

        Guides the multi-turn conversation toward the goal.
        """
        details = {
            "current_state": current_state,
            "goal": goal,
            "steps_taken": current_state.get("steps_completed", []),
        }

        recommendations = []

        # Analyze current state
        has_data = bool(current_state.get("data_collected"))
        has_structure = bool(current_state.get("structure_identified"))
        has_validation = bool(current_state.get("validation_complete"))
        has_analysis = bool(current_state.get("analysis_performed"))

        # Determine next steps based on state
        if not has_data:
            recommendations.append(
                "1️⃣ First: Get basic file information (get_excel_info)"
            )
            recommendations.append(
                "2️⃣ Then: Visualize data structure (show_excel_visual)"
            )
            confidence = 0.9
            summary = "Start with data exploration"

        elif not has_structure:
            recommendations.append(
                "1️⃣ Identify account structure (find_account or get_financial_overview)"
            )
            recommendations.append("2️⃣ Understand hierarchies (get_account_hierarchy)")
            confidence = 0.85
            summary = "Map financial structure"

        elif not has_validation:
            recommendations.append("1️⃣ Validate account structure with user")
            recommendations.append("2️⃣ Confirm calculation assumptions")
            confidence = 0.9
            summary = "Validate before analysis"

        elif not has_analysis:
            recommendations.append("1️⃣ Perform calculations on validated accounts")
            recommendations.append("2️⃣ Generate insights and recommendations")
            confidence = 0.9
            summary = "Proceed with analysis"

        else:
            recommendations.append("✅ Analysis appears complete")
            recommendations.append("Consider: Additional insights or reporting")
            confidence = 0.95
            summary = "Analysis workflow complete"

        result = ThinkingResult(
            thought_type="next_steps",
            summary=summary,
            details=details,
            recommendations=recommendations,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
        )

        self.thought_history.append(result)
        return result

    def think_about_data_quality(self, data: Dict[str, Any]) -> ThinkingResult:
        """
        Assess quality and reliability of financial data.

        Identifies potential issues or anomalies.
        """
        details = {"data_summary": {}}
        issues = []
        recommendations = []

        # Check for missing values
        for key, value in data.items():
            if value is None or (isinstance(value, float) and value == 0):
                issues.append(f"Missing or zero value for {key}")

        # Check for suspicious patterns
        values = [v for v in data.values() if isinstance(v, (int, float))]
        if values:
            details["value_count"] = len(values)
            details["value_range"] = {"min": min(values), "max": max(values)}

            # Check for outliers (simple heuristic)
            avg = sum(values) / len(values)
            for key, value in data.items():
                if isinstance(value, (int, float)) and abs(value) > avg * 10:
                    issues.append(f"Potential outlier: {key} = {value}")

        if issues:
            confidence = 0.6
            summary = f"Data quality concerns: {len(issues)} issues found"
            recommendations.append("⚠️ Review data quality issues:")
            recommendations.extend([f"  - {issue}" for issue in issues[:5]])  # Top 5
        else:
            confidence = 0.9
            summary = "Data quality appears good"
            recommendations.append("✅ No obvious data quality issues")

        details["issues"] = issues

        result = ThinkingResult(
            thought_type="data_quality",
            summary=summary,
            details=details,
            recommendations=recommendations,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
        )

        self.thought_history.append(result)
        return result

    def _assess_completeness(self, data: Dict[str, Any]) -> float:
        """Assess data completeness (0.0 to 1.0)."""
        if not data:
            return 0.0

        # Count non-null, non-empty values
        valid_count = sum(1 for v in data.values() if v is not None and v != "")
        return valid_count / len(data)

    def _validate_assumption(
        self, key: str, value: Any, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a single assumption."""
        # Default validation
        result = {"valid": True, "reason": "Assumption accepted"}

        # Specific validations
        if "depreciation" in key.lower() or "摊销" in key:
            if isinstance(value, (int, float)):
                if value < 1 or value > 10:
                    result = {
                        "valid": False,
                        "reason": f"Depreciation period {value} years is unusual (typically 3-5 years)",
                    }

        elif "percentage" in key.lower() or "rate" in key.lower():
            if isinstance(value, (int, float)):
                if value < 0 or value > 100:
                    result = {
                        "valid": False,
                        "reason": f"Percentage {value}% is out of valid range (0-100%)",
                    }

        return result

    def get_thought_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent thinking history."""
        return [t.to_dict() for t in self.thought_history[-limit:]]

    def clear_history(self) -> None:
        """Clear thinking history."""
        self.thought_history.clear()


# Global instance
thinking_tools = FinancialThinkingTools()
