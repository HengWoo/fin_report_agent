"""
Test suite for ValidationStateManager following TDD methodology.

These tests define the exact behavior required for validation state management.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
import json

from src.mcp_server.validation_state import (
    ValidationStateManager,
    ValidationSession,
    ValidationAssumption,
    ValidationStatus
)


class TestValidationAssumption:
    """Test ValidationAssumption data class."""

    def test_create_assumption_with_defaults(self):
        """Test creating assumption with default values."""
        assumption = ValidationAssumption(
            key="test_key",
            description="Test assumption",
            value="test_value",
            status=ValidationStatus.PENDING
        )

        assert assumption.key == "test_key"
        assert assumption.description == "Test assumption"
        assert assumption.value == "test_value"
        assert assumption.status == ValidationStatus.PENDING
        assert assumption.confirmed_at is None
        assert assumption.expires_at is None

    def test_assumption_is_valid_when_confirmed(self):
        """Test that confirmed assumption without expiry is valid."""
        assumption = ValidationAssumption(
            key="test",
            description="Test",
            value="value",
            status=ValidationStatus.CONFIRMED
        )

        assert assumption.is_valid() is True

    def test_assumption_is_invalid_when_pending(self):
        """Test that pending assumption is invalid."""
        assumption = ValidationAssumption(
            key="test",
            description="Test",
            value="value",
            status=ValidationStatus.PENDING
        )

        assert assumption.is_valid() is False

    def test_assumption_expires(self):
        """Test that assumption expires when past expiry time."""
        past_time = (datetime.now() - timedelta(hours=1)).isoformat()

        assumption = ValidationAssumption(
            key="test",
            description="Test",
            value="value",
            status=ValidationStatus.CONFIRMED,
            expires_at=past_time
        )

        assert assumption.is_valid() is False
        assert assumption.status == ValidationStatus.EXPIRED

    def test_assumption_to_dict(self):
        """Test converting assumption to dictionary."""
        assumption = ValidationAssumption(
            key="test_key",
            description="Test assumption",
            value={"nested": "value"},
            status=ValidationStatus.CONFIRMED
        )

        result = assumption.to_dict()

        assert result["key"] == "test_key"
        assert result["description"] == "Test assumption"
        assert result["value"] == {"nested": "value"}
        assert result["status"] == ValidationStatus.CONFIRMED


class TestValidationSession:
    """Test ValidationSession data class."""

    def test_create_session_with_defaults(self):
        """Test creating session with default values."""
        session = ValidationSession(
            session_id="test_session",
            file_path="/path/to/file.xlsx"
        )

        assert session.session_id == "test_session"
        assert session.file_path == "/path/to/file.xlsx"
        assert session.account_structure_confirmed is False
        assert session.depreciation_periods_confirmed is False
        assert session.safe_accounts_confirmed is False
        assert session.benchmark_preferences_confirmed is False
        assert session.assumptions == {}
        assert session.created_at is not None
        assert session.last_updated is not None

    def test_session_not_fully_validated_by_default(self):
        """Test that new session is not fully validated."""
        session = ValidationSession(
            session_id="test",
            file_path="/path/file.xlsx"
        )

        assert session.is_fully_validated() is False

    def test_session_fully_validated_when_all_confirmed(self):
        """Test that session is fully validated when all confirmations are true."""
        session = ValidationSession(
            session_id="test",
            file_path="/path/file.xlsx"
        )

        # Confirm all required validations
        session.account_structure_confirmed = True
        session.depreciation_periods_confirmed = True
        session.safe_accounts_confirmed = True

        assert session.is_fully_validated() is True

    def test_add_assumption(self):
        """Test adding assumption to session."""
        session = ValidationSession(
            session_id="test",
            file_path="/path/file.xlsx"
        )

        assumption = session.add_assumption(
            key="depreciation_period",
            description="Equipment depreciation period",
            value=3,
            expires_in_hours=24
        )

        assert assumption.key == "depreciation_period"
        assert assumption.description == "Equipment depreciation period"
        assert assumption.value == 3
        assert assumption.status == ValidationStatus.PENDING
        assert assumption.expires_at is not None

        assert "depreciation_period" in session.assumptions

    def test_confirm_assumption(self):
        """Test confirming an assumption."""
        session = ValidationSession(
            session_id="test",
            file_path="/path/file.xlsx"
        )

        session.add_assumption("test_key", "Test", "value")
        result = session.confirm_assumption("test_key")

        assert result is True
        assert session.assumptions["test_key"].status == ValidationStatus.CONFIRMED
        assert session.assumptions["test_key"].confirmed_at is not None

    def test_confirm_nonexistent_assumption(self):
        """Test confirming non-existent assumption returns False."""
        session = ValidationSession(
            session_id="test",
            file_path="/path/file.xlsx"
        )

        result = session.confirm_assumption("nonexistent")

        assert result is False

    def test_reject_assumption(self):
        """Test rejecting an assumption."""
        session = ValidationSession(
            session_id="test",
            file_path="/path/file.xlsx"
        )

        session.add_assumption("test_key", "Test", "value")
        result = session.reject_assumption("test_key")

        assert result is True
        assert session.assumptions["test_key"].status == ValidationStatus.REJECTED

    def test_get_validation_summary(self):
        """Test getting validation summary."""
        session = ValidationSession(
            session_id="test_session",
            file_path="/path/file.xlsx"
        )

        session.account_structure_confirmed = True
        session.add_assumption("test", "Test assumption", "value")
        session.confirm_assumption("test")

        summary = session.get_validation_summary()

        assert summary["session_id"] == "test_session"
        assert summary["file_path"] == "/path/file.xlsx"
        assert summary["validations"]["account_structure"] is True
        assert summary["validations"]["depreciation_periods"] is False
        assert summary["assumptions_count"] == 1
        assert summary["valid_assumptions"] == 1


class TestValidationStateManager:
    """Test ValidationStateManager main functionality."""

    def setup_method(self):
        """Setup fresh manager for each test."""
        self.manager = ValidationStateManager(session_timeout_hours=1)

    def test_create_session(self):
        """Test creating a new validation session."""
        file_path = "/path/to/restaurant_data.xlsx"

        session = self.manager.create_session(file_path)

        assert session.file_path == file_path
        assert session.session_id.startswith("session_")
        assert session.session_id in self.manager.sessions

    def test_get_session_for_file(self):
        """Test retrieving session for a file."""
        file_path = "/path/to/restaurant_data.xlsx"

        # Create session
        original_session = self.manager.create_session(file_path)

        # Retrieve session
        retrieved_session = self.manager.get_session_for_file(file_path)

        assert retrieved_session is not None
        assert retrieved_session.session_id == original_session.session_id

    def test_get_session_for_nonexistent_file(self):
        """Test retrieving session for non-existent file returns None."""
        result = self.manager.get_session_for_file("/nonexistent/file.xlsx")

        assert result is None

    def test_get_or_create_session_creates_new(self):
        """Test get_or_create creates new session when none exists."""
        file_path = "/path/to/new_file.xlsx"

        session = self.manager.get_or_create_session(file_path)

        assert session.file_path == file_path
        assert session.session_id in self.manager.sessions

    def test_get_or_create_session_returns_existing(self):
        """Test get_or_create returns existing session when available."""
        file_path = "/path/to/existing_file.xlsx"

        # Create original session
        original_session = self.manager.create_session(file_path)

        # Get or create should return the existing one
        retrieved_session = self.manager.get_or_create_session(file_path)

        assert retrieved_session.session_id == original_session.session_id

    def test_can_proceed_with_calculation_no_session(self):
        """Test calculation check when no session exists."""
        can_proceed, missing = self.manager.can_proceed_with_calculation("/nonexistent.xlsx")

        assert can_proceed is False
        assert "No validation session found" in missing[0]

    def test_can_proceed_with_calculation_incomplete_validation(self):
        """Test calculation check with incomplete validation."""
        file_path = "/path/to/file.xlsx"
        session = self.manager.create_session(file_path)

        # Only confirm one validation
        session.account_structure_confirmed = True

        can_proceed, missing = self.manager.can_proceed_with_calculation(file_path)

        assert can_proceed is False
        assert "Depreciation periods not confirmed" in missing
        assert "Safe accounts selection not confirmed" in missing

    def test_can_proceed_with_calculation_fully_validated(self):
        """Test calculation check with complete validation."""
        file_path = "/path/to/file.xlsx"
        session = self.manager.create_session(file_path)

        # Confirm all validations
        session.account_structure_confirmed = True
        session.depreciation_periods_confirmed = True
        session.safe_accounts_confirmed = True

        can_proceed, missing = self.manager.can_proceed_with_calculation(file_path)

        assert can_proceed is True
        assert missing == []

    def test_confirm_account_structure(self):
        """Test confirming account structure for a session."""
        session = self.manager.create_session("/path/file.xlsx")
        hierarchy_result = {
            "total_accounts": 50,
            "safe_accounts": ["账户1", "账户2"],
            "validation_flags": {"potential_double_counting": []}
        }

        result = self.manager.confirm_account_structure(session.session_id, hierarchy_result)

        assert result is True
        assert session.account_structure_confirmed is True
        assert "hierarchy_structure" in session.assumptions

    def test_confirm_account_structure_invalid_session(self):
        """Test confirming account structure with invalid session ID."""
        result = self.manager.confirm_account_structure("invalid_session", {})

        assert result is False

    def test_confirm_depreciation_periods(self):
        """Test confirming depreciation periods."""
        session = self.manager.create_session("/path/file.xlsx")
        periods = {"设备": 3, "装修": 5}

        result = self.manager.confirm_depreciation_periods(session.session_id, periods)

        assert result is True
        assert session.depreciation_periods_confirmed is True
        assert "depreciation_设备" in session.assumptions
        assert "depreciation_装修" in session.assumptions

    def test_confirm_safe_accounts(self):
        """Test confirming safe accounts selection."""
        session = self.manager.create_session("/path/file.xlsx")
        accounts = ["账户A", "账户B", "账户C"]

        result = self.manager.confirm_safe_accounts(session.session_id, accounts)

        assert result is True
        assert session.safe_accounts_confirmed is True
        assert "safe_accounts_selection" in session.assumptions

    def test_confirm_benchmark_preferences(self):
        """Test confirming benchmark preferences."""
        session = self.manager.create_session("/path/file.xlsx")
        benchmarks = {"food_cost_target": 0.30, "labor_cost_target": 0.25}

        result = self.manager.confirm_benchmark_preferences(session.session_id, benchmarks)

        assert result is True
        assert session.benchmark_preferences_confirmed is True
        assert "benchmark_preferences" in session.assumptions

    def test_get_session_assumptions(self):
        """Test retrieving session assumptions."""
        session = self.manager.create_session("/path/file.xlsx")
        session.add_assumption("test_key", "Test assumption", "test_value")

        assumptions = self.manager.get_session_assumptions(session.session_id)

        assert "test_key" in assumptions
        assert assumptions["test_key"]["description"] == "Test assumption"

    def test_get_session_assumptions_invalid_session(self):
        """Test retrieving assumptions for invalid session."""
        assumptions = self.manager.get_session_assumptions("invalid_session")

        assert assumptions == {}

    def test_generate_validation_report(self):
        """Test generating validation report."""
        session = self.manager.create_session("/path/file.xlsx")
        session.account_structure_confirmed = True
        session.add_assumption("test", "Test assumption", "value")
        session.confirm_assumption("test")

        report = self.manager.generate_validation_report(session.session_id)

        assert "Validation Report" in report
        assert session.session_id in report
        assert "✅ Fully Validated" in report or "⚠️ Incomplete Validation" in report
        assert "Account Structure: ✅" in report

    def test_generate_validation_report_invalid_session(self):
        """Test generating report for invalid session."""
        report = self.manager.generate_validation_report("invalid_session")

        assert "❌ Session not found" in report

    def test_export_session_state(self):
        """Test exporting session state."""
        session = self.manager.create_session("/path/file.xlsx")
        session.account_structure_confirmed = True

        exported = self.manager.export_session_state(session.session_id)

        assert exported is not None
        assert "session" in exported
        assert "exported_at" in exported
        assert exported["session"]["session_id"] == session.session_id

    def test_export_session_state_invalid_session(self):
        """Test exporting state for invalid session."""
        exported = self.manager.export_session_state("invalid_session")

        assert exported is None

    def test_import_session_state(self):
        """Test importing session state."""
        # Create and export a session
        original_session = self.manager.create_session("/path/file.xlsx")
        original_session.account_structure_confirmed = True
        exported_data = self.manager.export_session_state(original_session.session_id)

        # Clear sessions and import
        self.manager.sessions.clear()
        result = self.manager.import_session_state(exported_data)

        assert result is True
        assert original_session.session_id in self.manager.sessions
        restored_session = self.manager.sessions[original_session.session_id]
        assert restored_session.account_structure_confirmed is True


class TestValidationStateManagerIntegration:
    """Integration tests for complete validation workflow."""

    def setup_method(self):
        """Setup fresh manager for each test."""
        self.manager = ValidationStateManager()

    def test_complete_validation_workflow(self):
        """Test complete validation workflow from start to calculation."""
        file_path = "/path/to/restaurant_financial_data.xlsx"

        # Step 1: Create session
        session = self.manager.create_session(file_path)

        # Step 2: Confirm account structure
        hierarchy_result = {
            "total_accounts": 25,
            "safe_accounts": ["食品成本", "人工成本"],
            "validation_flags": {"potential_double_counting": []}
        }
        self.manager.confirm_account_structure(session.session_id, hierarchy_result)

        # Step 3: Confirm depreciation periods
        self.manager.confirm_depreciation_periods(session.session_id, {"装修": 3, "设备": 5})

        # Step 4: Confirm safe accounts
        self.manager.confirm_safe_accounts(session.session_id, ["食品成本", "人工成本"])

        # Step 5: Confirm benchmark preferences
        self.manager.confirm_benchmark_preferences(session.session_id, {"food_cost": 0.30})

        # Step 6: Check if calculation can proceed
        can_proceed, missing = self.manager.can_proceed_with_calculation(file_path)

        assert can_proceed is True
        assert missing == []
        assert session.is_fully_validated() is True

    def test_blocked_calculation_workflow(self):
        """Test workflow where calculation is blocked due to missing validation."""
        file_path = "/path/to/incomplete_validation.xlsx"

        # Create session but only partial validation
        session = self.manager.create_session(file_path)
        self.manager.confirm_account_structure(session.session_id, {"total_accounts": 10})
        # Skip other confirmations

        # Check if calculation can proceed
        can_proceed, missing = self.manager.can_proceed_with_calculation(file_path)

        assert can_proceed is False
        assert len(missing) > 0
        assert "Depreciation periods not confirmed" in missing
        assert "Safe accounts selection not confirmed" in missing

    def test_assumption_expiry_workflow(self):
        """Test workflow with expired assumptions."""
        file_path = "/path/to/expired_validation.xlsx"

        session = self.manager.create_session(file_path)

        # Add assumption that expires immediately
        assumption = session.add_assumption("test", "Test", "value", expires_in_hours=0)
        session.confirm_assumption("test")

        # Confirm other validations
        session.account_structure_confirmed = True
        session.depreciation_periods_confirmed = True
        session.safe_accounts_confirmed = True

        # Check calculation (should fail due to expired assumption)
        can_proceed, missing = self.manager.can_proceed_with_calculation(file_path)

        assert can_proceed is False
        assert any("Assumption expired" in msg for msg in missing)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])