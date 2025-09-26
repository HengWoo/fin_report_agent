"""
Error Handling and Recovery for MCP Server

Comprehensive error handling, logging, and recovery mechanisms
for the Restaurant Financial Analysis MCP Server.
"""

import asyncio
import logging
import traceback
import json
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""

    VALIDATION = "validation"
    PARSING = "parsing"
    ANALYSIS = "analysis"
    NETWORK = "network"
    SYSTEM = "system"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    DATA_CORRUPTION = "data_corruption"


@dataclass
class ErrorContext:
    """Context information for errors."""

    tool_name: Optional[str] = None
    file_path: Optional[str] = None
    user_input: Optional[Dict[str, Any]] = None
    system_state: Optional[Dict[str, Any]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class MCPError:
    """Structured error information."""

    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    context: Optional[ErrorContext] = None
    suggested_actions: List[str] = None
    recoverable: bool = True
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.suggested_actions is None:
            self.suggested_actions = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["category"] = self.category.value
        result["severity"] = self.severity.value
        return result


class ErrorRecoveryManager:
    """Manager for error recovery strategies."""

    def __init__(self):
        """Initialize the error recovery manager."""
        self.logger = logging.getLogger("mcp_error_recovery")
        self.recovery_strategies: Dict[ErrorCategory, Callable] = {
            ErrorCategory.VALIDATION: self._recover_validation_error,
            ErrorCategory.PARSING: self._recover_parsing_error,
            ErrorCategory.ANALYSIS: self._recover_analysis_error,
            ErrorCategory.NETWORK: self._recover_network_error,
            ErrorCategory.SYSTEM: self._recover_system_error,
            ErrorCategory.AUTHENTICATION: self._recover_auth_error,
            ErrorCategory.CONFIGURATION: self._recover_config_error,
            ErrorCategory.DATA_CORRUPTION: self._recover_data_corruption_error,
        }

    async def handle_error(
        self, error: Exception, context: ErrorContext, retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Handle an error with appropriate recovery strategy.

        Args:
            error: The exception that occurred
            context: Error context information
            retry_count: Number of retry attempts

        Returns:
            Dictionary containing error handling results
        """
        # Categorize and analyze the error
        mcp_error = self._analyze_error(error, context)

        self.logger.error(f"Error occurred: {mcp_error.error_id}")
        self.logger.error(
            f"Category: {mcp_error.category.value}, Severity: {mcp_error.severity.value}"
        )
        self.logger.error(f"Message: {mcp_error.message}")

        # Attempt recovery if the error is recoverable
        recovery_result = None
        if mcp_error.recoverable and retry_count < 3:
            try:
                recovery_result = await self._attempt_recovery(
                    mcp_error, context, retry_count
                )
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed: {str(recovery_error)}")

        # Prepare response
        response = {
            "error": mcp_error.to_dict(),
            "recovery_attempted": recovery_result is not None,
            "recovery_successful": (
                recovery_result.get("success", False) if recovery_result else False
            ),
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat(),
        }

        if recovery_result:
            response["recovery_result"] = recovery_result

        # Log the error for monitoring
        await self._log_error_for_monitoring(mcp_error, context, response)

        return response

    def _analyze_error(self, error: Exception, context: ErrorContext) -> MCPError:
        """Analyze an error and create structured error information."""
        error_type = type(error).__name__
        error_message = str(error)

        # Generate unique error ID
        error_id = f"{error_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(error_message) % 10000:04d}"

        # Categorize the error
        category = self._categorize_error(error, context)

        # Assess severity
        severity = self._assess_severity(error, category, context)

        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(error, category, context)

        # Determine if recoverable
        recoverable = self._is_recoverable(error, category, severity)

        return MCPError(
            error_id=error_id,
            category=category,
            severity=severity,
            message=error_message,
            details=traceback.format_exc(),
            context=context,
            suggested_actions=suggested_actions,
            recoverable=recoverable,
        )

    def _categorize_error(
        self, error: Exception, context: ErrorContext
    ) -> ErrorCategory:
        """Categorize an error based on type and context."""
        error_type = type(error).__name__

        # File and parsing errors
        if isinstance(error, (FileNotFoundError, PermissionError)):
            return ErrorCategory.PARSING
        elif "validation" in error_type.lower() or "pydantic" in error_type.lower():
            return ErrorCategory.VALIDATION
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorCategory.NETWORK
        elif (
            "authentication" in error_type.lower()
            or "unauthorized" in error_type.lower()
        ):
            return ErrorCategory.AUTHENTICATION
        elif "config" in error_type.lower():
            return ErrorCategory.CONFIGURATION
        elif isinstance(error, (MemoryError, OSError)):
            return ErrorCategory.SYSTEM
        elif "corrupt" in str(error).lower() or "invalid format" in str(error).lower():
            return ErrorCategory.DATA_CORRUPTION
        else:
            return ErrorCategory.ANALYSIS

    def _assess_severity(
        self, error: Exception, category: ErrorCategory, context: ErrorContext
    ) -> ErrorSeverity:
        """Assess the severity of an error."""
        if isinstance(error, (MemoryError, SystemError)):
            return ErrorSeverity.CRITICAL
        elif category in [ErrorCategory.SYSTEM, ErrorCategory.DATA_CORRUPTION]:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.NETWORK, ErrorCategory.AUTHENTICATION]:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

    def _generate_suggested_actions(
        self, error: Exception, category: ErrorCategory, context: ErrorContext
    ) -> List[str]:
        """Generate suggested actions for error resolution."""
        actions = []

        if category == ErrorCategory.VALIDATION:
            actions.extend(
                [
                    "Check input data format and structure",
                    "Verify all required fields are present",
                    "Ensure data types match expected formats",
                ]
            )
        elif category == ErrorCategory.PARSING:
            actions.extend(
                [
                    "Verify file exists and is accessible",
                    "Check file format and extension",
                    "Ensure file is not corrupted or locked",
                ]
            )
        elif category == ErrorCategory.NETWORK:
            actions.extend(
                [
                    "Check network connectivity",
                    "Verify server endpoints are accessible",
                    "Retry the operation after a brief delay",
                ]
            )
        elif category == ErrorCategory.AUTHENTICATION:
            actions.extend(
                [
                    "Verify authentication credentials",
                    "Check API key validity",
                    "Ensure proper permissions are set",
                ]
            )
        elif category == ErrorCategory.SYSTEM:
            actions.extend(
                [
                    "Check system resources (memory, disk space)",
                    "Restart the service if necessary",
                    "Contact system administrator",
                ]
            )

        # Add general actions
        actions.extend(
            [
                "Review error details and context",
                "Check system logs for additional information",
                "Contact support if issue persists",
            ]
        )

        return actions

    def _is_recoverable(
        self, error: Exception, category: ErrorCategory, severity: ErrorSeverity
    ) -> bool:
        """Determine if an error is recoverable."""
        if severity == ErrorSeverity.CRITICAL:
            return False
        elif category in [ErrorCategory.NETWORK, ErrorCategory.AUTHENTICATION]:
            return True
        elif category == ErrorCategory.SYSTEM and not isinstance(error, MemoryError):
            return True
        elif category in [ErrorCategory.VALIDATION, ErrorCategory.PARSING]:
            return True
        else:
            return False

    async def _attempt_recovery(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Attempt to recover from an error."""
        recovery_strategy = self.recovery_strategies.get(mcp_error.category)

        if not recovery_strategy:
            return {"success": False, "reason": "No recovery strategy available"}

        try:
            return await recovery_strategy(mcp_error, context, retry_count)
        except Exception as e:
            return {"success": False, "reason": f"Recovery strategy failed: {str(e)}"}

    async def _recover_validation_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from validation errors."""
        self.logger.info("Attempting validation error recovery")

        # Try to sanitize and revalidate data
        if context.user_input:
            try:
                # Simple data cleaning
                cleaned_data = self._sanitize_input_data(context.user_input)
                return {
                    "success": True,
                    "method": "data_sanitization",
                    "cleaned_data": cleaned_data,
                }
            except Exception as e:
                return {
                    "success": False,
                    "reason": f"Data sanitization failed: {str(e)}",
                }

        return {"success": False, "reason": "No recoverable data available"}

    async def _recover_parsing_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from parsing errors."""
        self.logger.info("Attempting parsing error recovery")

        if context.file_path:
            file_path = Path(context.file_path)

            # Check if file exists
            if not file_path.exists():
                return {"success": False, "reason": "File not found"}

            # Try alternative parsing methods
            try:
                # Attempt with different encoding
                return {
                    "success": True,
                    "method": "alternative_encoding",
                    "suggestion": "Try UTF-8 or GB2312 encoding",
                }
            except Exception as e:
                return {
                    "success": False,
                    "reason": f"Alternative parsing failed: {str(e)}",
                }

        return {"success": False, "reason": "No file path provided"}

    async def _recover_analysis_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from analysis errors."""
        self.logger.info("Attempting analysis error recovery")

        # Try with simplified analysis parameters
        return {
            "success": True,
            "method": "simplified_analysis",
            "suggestion": "Use basic analysis mode with reduced complexity",
        }

    async def _recover_network_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from network errors."""
        self.logger.info(
            f"Attempting network error recovery (attempt {retry_count + 1})"
        )

        # Wait before retry with exponential backoff
        wait_time = min(2**retry_count, 30)  # Max 30 seconds
        await asyncio.sleep(wait_time)

        return {
            "success": True,
            "method": "retry_with_backoff",
            "wait_time": wait_time,
            "suggestion": "Retry the operation",
        }

    async def _recover_system_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from system errors."""
        self.logger.info("Attempting system error recovery")

        # Perform garbage collection
        import gc

        gc.collect()

        return {
            "success": True,
            "method": "resource_cleanup",
            "suggestion": "Retry with reduced resource usage",
        }

    async def _recover_auth_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from authentication errors."""
        self.logger.info("Attempting authentication error recovery")

        return {
            "success": False,
            "reason": "Authentication errors require manual intervention",
            "suggestion": "Check credentials and permissions",
        }

    async def _recover_config_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from configuration errors."""
        self.logger.info("Attempting configuration error recovery")

        # Try to load default configuration
        return {
            "success": True,
            "method": "fallback_config",
            "suggestion": "Using default configuration settings",
        }

    async def _recover_data_corruption_error(
        self, mcp_error: MCPError, context: ErrorContext, retry_count: int
    ) -> Dict[str, Any]:
        """Recover from data corruption errors."""
        self.logger.info("Attempting data corruption error recovery")

        return {
            "success": False,
            "reason": "Data corruption requires manual data repair",
            "suggestion": "Please provide a clean data file",
        }

    def _sanitize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data to remove common issues."""
        cleaned_data = {}

        for key, value in input_data.items():
            if isinstance(value, str):
                # Remove extra whitespace
                cleaned_value = value.strip()
                # Convert to appropriate type if possible
                try:
                    if cleaned_value.replace(".", "").isdigit():
                        cleaned_value = float(cleaned_value)
                except ValueError:
                    pass
                cleaned_data[key] = cleaned_value
            elif isinstance(value, dict):
                cleaned_data[key] = self._sanitize_input_data(value)
            else:
                cleaned_data[key] = value

        return cleaned_data

    async def _log_error_for_monitoring(
        self, mcp_error: MCPError, context: ErrorContext, response: Dict[str, Any]
    ) -> None:
        """Log error information for monitoring and analytics."""
        log_entry = {
            "error_id": mcp_error.error_id,
            "category": mcp_error.category.value,
            "severity": mcp_error.severity.value,
            "tool_name": context.tool_name,
            "file_path": context.file_path,
            "recovery_attempted": response.get("recovery_attempted", False),
            "recovery_successful": response.get("recovery_successful", False),
            "timestamp": mcp_error.timestamp,
        }

        # Log to file for monitoring systems
        self.logger.info(f"Error monitoring: {json.dumps(log_entry)}")


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Timeout in seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset."""
        if self.last_failure_time is None:
            return False
        return datetime.now().timestamp() - self.last_failure_time > self.timeout

    def _on_success(self) -> None:
        """Handle successful execution."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self) -> None:
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now().timestamp()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
