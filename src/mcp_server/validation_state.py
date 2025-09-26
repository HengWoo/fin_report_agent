"""
Validation State Manager for Financial Analysis

This module manages validation state throughout the analysis session,
preventing calculations from proceeding without user confirmation.
Following Serena's pattern of stateful validation management.

Features:
- Session-based validation tracking
- Assumption expiration and auto-cleanup
- Comprehensive validation reporting
- State persistence and restoration
- Thread-safe operations
"""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


class ValidationStatus(Enum):
    """Validation status states."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ValidationAssumption:
    """Individual validation assumption."""

    key: str
    description: str
    value: Any
    status: ValidationStatus
    confirmed_at: Optional[str] = None
    expires_at: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if assumption is still valid."""
        if self.status != ValidationStatus.CONFIRMED:
            return False

        if self.expires_at:
            expiry = datetime.fromisoformat(self.expires_at)
            if datetime.now() > expiry:
                self.status = ValidationStatus.EXPIRED
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ValidationSession:
    """Validation session tracking user confirmations."""

    session_id: str
    file_path: str
    account_structure_confirmed: bool = False
    depreciation_periods_confirmed: bool = False
    safe_accounts_confirmed: bool = False
    benchmark_preferences_confirmed: bool = False
    assumptions: Dict[str, ValidationAssumption] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    # Additional metadata for enhanced functionality
    user_context: Dict[str, Any] = field(default_factory=dict)
    validation_history: List[str] = field(default_factory=list)

    def is_fully_validated(self) -> bool:
        """Check if all required validations are complete."""
        return (
            self.account_structure_confirmed
            and self.depreciation_periods_confirmed
            and self.safe_accounts_confirmed
            and all(assumption.is_valid() for assumption in self.assumptions.values())
        )

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation status summary."""
        return {
            "session_id": self.session_id,
            "file_path": self.file_path,
            "fully_validated": self.is_fully_validated(),
            "validations": {
                "account_structure": self.account_structure_confirmed,
                "depreciation_periods": self.depreciation_periods_confirmed,
                "safe_accounts": self.safe_accounts_confirmed,
                "benchmark_preferences": self.benchmark_preferences_confirmed,
            },
            "assumptions_count": len(self.assumptions),
            "valid_assumptions": sum(
                1 for a in self.assumptions.values() if a.is_valid()
            ),
            "last_updated": self.last_updated,
        }

    def add_assumption(
        self, key: str, description: str, value: Any, expires_in_hours: int = 24
    ) -> ValidationAssumption:
        """Add a new validation assumption."""
        expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()

        assumption = ValidationAssumption(
            key=key,
            description=description,
            value=value,
            status=ValidationStatus.PENDING,
            expires_at=expires_at,
        )

        self.assumptions[key] = assumption
        self.last_updated = datetime.now().isoformat()
        self._add_to_history(f"Added assumption: {key}")

        return assumption

    def confirm_assumption(self, key: str) -> bool:
        """Confirm an assumption."""
        if key in self.assumptions:
            self.assumptions[key].status = ValidationStatus.CONFIRMED
            self.assumptions[key].confirmed_at = datetime.now().isoformat()
            self.last_updated = datetime.now().isoformat()
            self._add_to_history(f"Confirmed assumption: {key}")
            return True
        return False

    def reject_assumption(self, key: str) -> bool:
        """Reject an assumption."""
        if key in self.assumptions:
            self.assumptions[key].status = ValidationStatus.REJECTED
            self.last_updated = datetime.now().isoformat()
            self._add_to_history(f"Rejected assumption: {key}")
            return True
        return False

    def _add_to_history(self, event: str) -> None:
        """Add event to validation history."""
        timestamp = datetime.now().isoformat()
        self.validation_history.append(f"[{timestamp}] {event}")

        # Keep only last 50 events to prevent memory bloat
        if len(self.validation_history) > 50:
            self.validation_history = self.validation_history[-50:]


class ValidationStateManager:
    """Manager for validation state across analysis sessions."""

    def __init__(self, session_timeout_hours: int = 24):
        """Initialize the validation state manager."""
        self.logger = logging.getLogger("validation_state")
        self.session_timeout_hours = session_timeout_hours
        self.sessions: Dict[str, ValidationSession] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Performance optimization
        self._file_to_session_cache: Dict[str, str] = {}

        self._cleanup_expired_sessions()

    def create_session(self, file_path: str) -> ValidationSession:
        """Create a new validation session."""
        with self._lock:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file_path) % 10000:04d}"

            session = ValidationSession(session_id=session_id, file_path=file_path)

            self.sessions[session_id] = session
            self._file_to_session_cache[file_path] = session_id
            self.logger.info(
                f"Created validation session: {session_id} for {file_path}"
            )

            return session

    def get_session_for_file(self, file_path: str) -> Optional[ValidationSession]:
        """Get the most recent valid session for a file."""
        with self._lock:
            # Try cache first for performance
            if file_path in self._file_to_session_cache:
                session_id = self._file_to_session_cache[file_path]
                if session_id in self.sessions:
                    return self.sessions[session_id]
                else:
                    # Cache is stale, remove it
                    del self._file_to_session_cache[file_path]

            # Fallback to full search
            matching_sessions = [
                session
                for session in self.sessions.values()
                if session.file_path == file_path
            ]

            if not matching_sessions:
                return None

            # Return the most recently updated session and update cache
            latest_session = max(matching_sessions, key=lambda s: s.last_updated)
            self._file_to_session_cache[file_path] = latest_session.session_id
            return latest_session

    def get_or_create_session(self, file_path: str) -> ValidationSession:
        """Get existing session or create new one."""
        session = self.get_session_for_file(file_path)

        if session is None:
            session = self.create_session(file_path)

        return session

    def can_proceed_with_calculation(self, file_path: str) -> tuple[bool, List[str]]:
        """Check if calculations can proceed for a file."""
        session = self.get_session_for_file(file_path)

        if session is None:
            return False, [
                "No validation session found. Must run validate_account_structure first."
            ]

        if session.is_fully_validated():
            return True, []

        # Collect missing validations
        missing = []

        if not session.account_structure_confirmed:
            missing.append("Account structure not confirmed")

        if not session.depreciation_periods_confirmed:
            missing.append("Depreciation periods not confirmed")

        if not session.safe_accounts_confirmed:
            missing.append("Safe accounts selection not confirmed")

        # Check expired assumptions
        expired_assumptions = [
            key
            for key, assumption in session.assumptions.items()
            if not assumption.is_valid()
        ]

        if expired_assumptions:
            missing.extend(
                [f"Assumption expired: {key}" for key in expired_assumptions]
            )

        return False, missing

    def confirm_account_structure(
        self, session_id: str, hierarchy_result: Dict[str, Any]
    ) -> bool:
        """Confirm account structure validation."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.account_structure_confirmed = True
        session.last_updated = datetime.now().isoformat()

        # Add key assumptions about the hierarchy
        session.add_assumption(
            "hierarchy_structure",
            "Account hierarchy structure and parent-child relationships",
            {
                "total_accounts": hierarchy_result.get("total_accounts", 0),
                "safe_accounts": len(hierarchy_result.get("safe_accounts", [])),
                "potential_double_counting": len(
                    hierarchy_result.get("validation_flags", {}).get(
                        "potential_double_counting", []
                    )
                ),
            },
        )

        # Auto-confirm the assumption since user is confirming the structure
        session.confirm_assumption("hierarchy_structure")

        self.logger.info(f"Account structure confirmed for session: {session_id}")
        return True

    def confirm_depreciation_periods(
        self, session_id: str, periods: Dict[str, int]
    ) -> bool:
        """Confirm depreciation periods."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.depreciation_periods_confirmed = True
        session.last_updated = datetime.now().isoformat()

        # Add depreciation assumptions
        for account, period in periods.items():
            session.add_assumption(
                f"depreciation_{account}", f"Depreciation period for {account}", period
            )
            # Auto-confirm each depreciation assumption
            session.confirm_assumption(f"depreciation_{account}")

        self.logger.info(f"Depreciation periods confirmed for session: {session_id}")
        return True

    def confirm_safe_accounts(
        self, session_id: str, selected_accounts: List[str]
    ) -> bool:
        """Confirm safe accounts selection."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.safe_accounts_confirmed = True
        session.last_updated = datetime.now().isoformat()

        # Add safe accounts assumption
        session.add_assumption(
            "safe_accounts_selection",
            "Selected accounts for calculations (leaf accounts only)",
            selected_accounts,
        )
        # Auto-confirm the assumption
        session.confirm_assumption("safe_accounts_selection")

        self.logger.info(f"Safe accounts confirmed for session: {session_id}")
        return True

    def confirm_benchmark_preferences(
        self, session_id: str, benchmarks: Dict[str, Any]
    ) -> bool:
        """Confirm benchmark preferences."""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.benchmark_preferences_confirmed = True
        session.last_updated = datetime.now().isoformat()

        # Add benchmark assumptions
        session.add_assumption(
            "benchmark_preferences",
            "Industry benchmark preferences and targets",
            benchmarks,
        )
        # Auto-confirm the assumption
        session.confirm_assumption("benchmark_preferences")

        self.logger.info(f"Benchmark preferences confirmed for session: {session_id}")
        return True

    def get_session_assumptions(self, session_id: str) -> Dict[str, Any]:
        """Get all assumptions for a session."""
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]
        return {
            key: assumption.to_dict() for key, assumption in session.assumptions.items()
        }

    def generate_validation_report(self, session_id: str) -> str:
        """Generate a comprehensive validation report."""
        if session_id not in self.sessions:
            return "❌ Session not found"

        session = self.sessions[session_id]
        summary = session.get_validation_summary()

        report = f"""
📋 **Validation Report for Session: {session_id}**
{'=' * 60}

**File:** {session.file_path}
**Status:** {'✅ Fully Validated' if summary['fully_validated'] else '⚠️ Incomplete Validation'}
**Last Updated:** {session.last_updated}

**Core Validations:**
- Account Structure: {'✅' if summary['validations']['account_structure'] else '❌'}
- Depreciation Periods: {'✅' if summary['validations']['depreciation_periods'] else '❌'}
- Safe Accounts: {'✅' if summary['validations']['safe_accounts'] else '❌'}
- Benchmark Preferences: {'✅' if summary['validations']['benchmark_preferences'] else '❌'}

**Assumptions ({summary['valid_assumptions']}/{summary['assumptions_count']} valid):**
"""

        for key, assumption in session.assumptions.items():
            status_icon = "✅" if assumption.is_valid() else "❌"
            report += f"- {status_icon} {assumption.description}: {assumption.value}\n"

        if not summary["fully_validated"]:
            can_proceed, missing = self.can_proceed_with_calculation(session.file_path)
            report += "\n**Missing Validations:**\n"
            for item in missing:
                report += f"- ❌ {item}\n"

        return report

    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        with self._lock:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=self.session_timeout_hours)

            expired_sessions = [
                session_id
                for session_id, session in self.sessions.items()
                if datetime.fromisoformat(session.last_updated) < cutoff_time
            ]

            for session_id in expired_sessions:
                session = self.sessions[session_id]
                # Clean up cache entries
                if session.file_path in self._file_to_session_cache:
                    if self._file_to_session_cache[session.file_path] == session_id:
                        del self._file_to_session_cache[session.file_path]

                del self.sessions[session_id]
                self.logger.info(f"Cleaned up expired session: {session_id}")

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics about current sessions."""
        with self._lock:
            total_sessions = len(self.sessions)
            fully_validated = sum(
                1 for s in self.sessions.values() if s.is_fully_validated()
            )
            total_assumptions = sum(len(s.assumptions) for s in self.sessions.values())

            return {
                "total_sessions": total_sessions,
                "fully_validated_sessions": fully_validated,
                "partially_validated_sessions": total_sessions - fully_validated,
                "total_assumptions": total_assumptions,
                "cache_size": len(self._file_to_session_cache),
                "oldest_session": min(
                    (
                        datetime.fromisoformat(s.created_at)
                        for s in self.sessions.values()
                    ),
                    default=None,
                ),
                "newest_session": max(
                    (
                        datetime.fromisoformat(s.created_at)
                        for s in self.sessions.values()
                    ),
                    default=None,
                ),
            }

    def export_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session state for persistence."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return {"session": asdict(session), "exported_at": datetime.now().isoformat()}

    def import_session_state(self, session_data: Dict[str, Any]) -> bool:
        """Import session state from persistence."""
        try:
            session_dict = session_data["session"]

            # Reconstruct assumptions
            assumptions = {}
            for key, assumption_dict in session_dict.get("assumptions", {}).items():
                assumption = ValidationAssumption(**assumption_dict)
                assumptions[key] = assumption

            session_dict["assumptions"] = assumptions

            session = ValidationSession(**session_dict)
            self.sessions[session.session_id] = session

            self.logger.info(f"Imported session state: {session.session_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import session state: {str(e)}")
            return False


# Global instance for the application
validation_state_manager = ValidationStateManager()
