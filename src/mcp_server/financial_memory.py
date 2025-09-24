"""
Financial Memory Manager for Multi-Turn Analysis

This module manages persistent memory for financial analysis sessions,
enabling Claude to maintain context across multiple conversation turns.
Inspired by Serena's memory system for intelligent conversation flow.

Features:
- Session-based memory storage
- Financial pattern recognition storage
- User preference tracking
- Analysis insight accumulation
- Domain knowledge persistence
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class AnalysisInsight:
    """Captured insight from financial analysis."""

    key: str
    description: str
    insight_type: str  # pattern, anomaly, recommendation, etc.
    context: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisSession:
    """Analysis session tracking conversation context."""

    session_id: str
    file_path: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())

    # Conversation context
    insights: List[AnalysisInsight] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    questions_asked: List[str] = field(default_factory=list)
    analysis_history: List[Dict[str, Any]] = field(default_factory=list)

    # Domain knowledge
    discovered_patterns: List[Dict[str, Any]] = field(default_factory=list)
    account_mappings: Dict[str, str] = field(default_factory=dict)

    def add_insight(
        self,
        key: str,
        description: str,
        insight_type: str,
        context: Dict[str, Any],
        confidence: float = 0.8,
    ) -> AnalysisInsight:
        """Add a new analysis insight."""
        insight = AnalysisInsight(
            key=key,
            description=description,
            insight_type=insight_type,
            context=context,
            confidence=confidence,
        )
        self.insights.append(insight)
        self.last_accessed = datetime.now().isoformat()
        return insight

    def add_to_history(self, action: str, details: Dict[str, Any]) -> None:
        """Add action to analysis history."""
        self.analysis_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details,
            }
        )
        self.last_accessed = datetime.now().isoformat()

    def get_recent_insights(self, limit: int = 5) -> List[AnalysisInsight]:
        """Get most recent insights."""
        return sorted(self.insights, key=lambda x: x.created_at, reverse=True)[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "file_path": self.file_path,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "insights": [i.to_dict() for i in self.insights],
            "user_preferences": self.user_preferences,
            "intermediate_results": self.intermediate_results,
            "questions_asked": self.questions_asked,
            "analysis_history": self.analysis_history,
            "discovered_patterns": self.discovered_patterns,
            "account_mappings": self.account_mappings,
        }


class FinancialMemoryManager:
    """Manager for financial analysis memory and session persistence."""

    def __init__(self, memory_dir: str = ".financial_memory"):
        """Initialize the memory manager."""
        self.logger = logging.getLogger("financial_memory")
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        # Session storage
        self.sessions: Dict[str, AnalysisSession] = {}

        # Global memory files
        self.insights_file = self.memory_dir / "insights.json"
        self.patterns_file = self.memory_dir / "patterns.json"
        self.preferences_file = self.memory_dir / "preferences.json"

        self._load_global_memory()

        # Global collections
        self.global_insights: List[AnalysisInsight] = []
        self.global_patterns: List[Dict[str, Any]] = []
        self.global_preferences: Dict[str, Any] = {}

    def _load_global_memory(self) -> None:
        """Load global memory files."""
        if self.insights_file.exists():
            with open(self.insights_file, "r") as f:
                data = json.load(f)
                self.global_insights = [AnalysisInsight(**i) for i in data]

        if self.patterns_file.exists():
            with open(self.patterns_file, "r") as f:
                self.global_patterns = json.load(f)

        if self.preferences_file.exists():
            with open(self.preferences_file, "r") as f:
                self.global_preferences = json.load(f)

    def _save_global_memory(self) -> None:
        """Save global memory files."""
        with open(self.insights_file, "w") as f:
            json.dump([i.to_dict() for i in self.global_insights], f, indent=2)

        with open(self.patterns_file, "w") as f:
            json.dump(self.global_patterns, f, indent=2)

        with open(self.preferences_file, "w") as f:
            json.dump(self.global_preferences, f, indent=2)

    def create_session(self, file_path: str) -> AnalysisSession:
        """Create a new analysis session."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file_path) % 10000:04d}"

        session = AnalysisSession(session_id=session_id, file_path=file_path)

        self.sessions[session_id] = session
        self.logger.info(f"Created analysis session: {session_id}")

        return session

    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def get_session_for_file(self, file_path: str) -> Optional[AnalysisSession]:
        """Get the most recent session for a file."""
        matching_sessions = [
            s for s in self.sessions.values() if s.file_path == file_path
        ]

        if not matching_sessions:
            return None

        return max(matching_sessions, key=lambda s: s.last_accessed)

    def get_or_create_session(self, file_path: str) -> AnalysisSession:
        """Get existing session or create new one."""
        session = self.get_session_for_file(file_path)

        if session is None:
            session = self.create_session(file_path)

        session.last_accessed = datetime.now().isoformat()
        return session

    def save_insight(
        self,
        session_id: str,
        key: str,
        description: str,
        insight_type: str,
        context: Dict[str, Any],
        confidence: float = 0.8,
        global_save: bool = True,
    ) -> bool:
        """Save an insight to session and optionally to global memory."""
        session = self.get_session(session_id)
        if not session:
            return False

        insight = session.add_insight(
            key, description, insight_type, context, confidence
        )

        if global_save and confidence >= 0.7:
            self.global_insights.append(insight)
            self._save_global_memory()

        self.logger.info(f"Saved insight: {key} to session {session_id}")
        return True

    def save_pattern(
        self, pattern: Dict[str, Any], session_id: Optional[str] = None
    ) -> bool:
        """Save a discovered financial pattern."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                session.discovered_patterns.append(pattern)

        self.global_patterns.append(pattern)
        self._save_global_memory()

        self.logger.info(f"Saved pattern: {pattern.get('name', 'unnamed')}")
        return True

    def save_preference(
        self, key: str, value: Any, session_id: Optional[str] = None
    ) -> bool:
        """Save a user preference."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                session.user_preferences[key] = value

        self.global_preferences[key] = value
        self._save_global_memory()

        self.logger.info(f"Saved preference: {key}")
        return True

    def get_insights(
        self,
        session_id: Optional[str] = None,
        insight_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[AnalysisInsight]:
        """Get insights from session or global memory."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                insights = session.insights
            else:
                insights = []
        else:
            insights = self.global_insights

        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]

        return sorted(insights, key=lambda x: x.created_at, reverse=True)[:limit]

    def get_patterns(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get patterns from session or global memory."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session.discovered_patterns
            return []

        return self.global_patterns

    def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of session context."""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session_id,
            "file_path": session.file_path,
            "created_at": session.created_at,
            "last_accessed": session.last_accessed,
            "insights_count": len(session.insights),
            "patterns_count": len(session.discovered_patterns),
            "history_count": len(session.analysis_history),
            "recent_insights": [i.to_dict() for i in session.get_recent_insights(3)],
            "user_preferences": session.user_preferences,
            "questions_asked_count": len(session.questions_asked),
        }

    def write_memory_file(
        self, name: str, content: str, session_id: Optional[str] = None
    ) -> bool:
        """Write a memory file (like Serena's memory system)."""
        try:
            memory_file = self.memory_dir / f"{name}.md"

            with open(memory_file, "w") as f:
                f.write(f"# {name}\n\n")
                f.write(f"Created: {datetime.now().isoformat()}\n\n")
                if session_id:
                    f.write(f"Session: {session_id}\n\n")
                f.write(content)

            self.logger.info(f"Wrote memory file: {name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to write memory file: {str(e)}")
            return False

    def read_memory_file(self, name: str) -> Optional[str]:
        """Read a memory file."""
        memory_file = self.memory_dir / f"{name}.md"

        if not memory_file.exists():
            return None

        with open(memory_file, "r") as f:
            return f.read()

    def list_memory_files(self) -> List[str]:
        """List all memory files."""
        return [f.stem for f in self.memory_dir.glob("*.md")]

    def export_session(
        self, session_id: str, export_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Export session to JSON file."""
        session = self.get_session(session_id)
        if not session:
            return None

        if export_path is None:
            export_path = self.memory_dir / f"{session_id}.json"

        with open(export_path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)

        self.logger.info(f"Exported session to: {export_path}")
        return export_path

    def import_session(self, import_path: Path) -> Optional[str]:
        """Import session from JSON file."""
        try:
            with open(import_path, "r") as f:
                data = json.load(f)

            insights = [AnalysisInsight(**i) for i in data.get("insights", [])]

            session = AnalysisSession(
                session_id=data["session_id"],
                file_path=data["file_path"],
                created_at=data["created_at"],
                last_accessed=data["last_accessed"],
                insights=insights,
                user_preferences=data.get("user_preferences", {}),
                intermediate_results=data.get("intermediate_results", {}),
                questions_asked=data.get("questions_asked", []),
                analysis_history=data.get("analysis_history", []),
                discovered_patterns=data.get("discovered_patterns", []),
                account_mappings=data.get("account_mappings", {}),
            )

            self.sessions[session.session_id] = session
            self.logger.info(f"Imported session: {session.session_id}")

            return session.session_id

        except Exception as e:
            self.logger.error(f"Failed to import session: {str(e)}")
            return None

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up sessions older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        removed_count = 0

        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            last_accessed = datetime.fromisoformat(session.last_accessed)
            if last_accessed < cutoff:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            removed_count += 1

        self.logger.info(f"Cleaned up {removed_count} old sessions")
        return removed_count


# Global instance
financial_memory_manager = FinancialMemoryManager()
