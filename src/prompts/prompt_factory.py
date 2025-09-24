"""
Prompt Factory for Claude-Orchestrated Financial Analysis

This module provides a dynamic prompt template system using Jinja2.
Templates are loaded from YAML files and can be hot-reloaded during development.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import threading

logger = logging.getLogger(__name__)


class PromptFileHandler(FileSystemEventHandler):
    """Handle file system events for hot reload."""

    def __init__(self, factory: 'PromptFactory'):
        self.factory = factory

    def on_modified(self, event: FileModifiedEvent):
        """Reload templates when YAML files are modified."""
        if not event.is_directory and event.src_path.endswith(('.yml', '.yaml')):
            logger.info(f"Reloading modified template: {event.src_path}")
            self.factory._load_single_template(event.src_path)


class PromptFactory:
    """
    Factory for managing and rendering prompt templates.

    Features:
    - Load templates from YAML files
    - Jinja2 templating with full feature support
    - Hot reload in development
    - Context accumulation
    - Template validation
    """

    def __init__(
        self,
        prompts_dir: str = "prompts/",
        enable_hot_reload: bool = True,
        context: str = "analysis"
    ):
        """
        Initialize the PromptFactory.

        Args:
            prompts_dir: Directory containing prompt templates
            enable_hot_reload: Enable file watching for hot reload
            context: Default context (exploration, analysis, validation)
        """
        self.prompts_dir = Path(prompts_dir).resolve()
        self.context = context
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self._setup_custom_filters()

        # Load configuration
        self._load_config()

        # Load all templates
        self._load_all_templates()

        # Setup hot reload if enabled
        self.observer = None
        if enable_hot_reload:
            self._setup_hot_reload()

        # Context accumulation for conversation flow
        self.conversation_context: List[Dict[str, Any]] = []

    def _setup_custom_filters(self):
        """Add custom Jinja2 filters for financial formatting."""

        def format_currency(value, symbol="¥"):
            """Format number as currency."""
            try:
                return f"{symbol}{float(value):,.2f}"
            except (ValueError, TypeError):
                return str(value)

        def format_percentage(value):
            """Format as percentage."""
            try:
                return f"{float(value):.2%}"
            except (ValueError, TypeError):
                return str(value)

        self.jinja_env.filters['currency'] = format_currency
        self.jinja_env.filters['percentage'] = format_percentage

    def _load_config(self):
        """Load configuration from config.yml."""
        config_path = self.prompts_dir / "config.yml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            logger.warning(f"Config file not found: {config_path}")
            self.config = {}

    def _load_all_templates(self):
        """Load all template files from the prompts directory."""
        template_dirs = [
            "templates/structure",
            "templates/accounting",
            "templates/extraction",
            "templates/validation",
            "contexts"
        ]

        for template_dir in template_dirs:
            dir_path = self.prompts_dir / template_dir
            if dir_path.exists():
                for file_path in dir_path.glob("*.yml"):
                    self._load_single_template(str(file_path))
                for file_path in dir_path.glob("*.yaml"):
                    self._load_single_template(str(file_path))

        logger.info(f"Loaded {len(self.templates)} prompt templates")

    def _load_single_template(self, file_path: str):
        """Load a single template file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if 'prompts' in data:
                prompts = data['prompts']
                for name, content in prompts.items():
                    if isinstance(content, dict):
                        # Structured template with metadata
                        self.templates[name] = {
                            'template': content.get('template', ''),
                            'description': content.get('description', ''),
                            'parameters': content.get('parameters', []),
                            'file_path': file_path
                        }
                    else:
                        # Simple template string
                        self.templates[name] = {
                            'template': content,
                            'description': '',
                            'parameters': [],
                            'file_path': file_path
                        }

            logger.debug(f"Loaded templates from {file_path}")

        except Exception as e:
            logger.error(f"Error loading template {file_path}: {e}")

    def _setup_hot_reload(self):
        """Setup file watching for hot reload."""
        event_handler = PromptFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(
            event_handler,
            str(self.prompts_dir),
            recursive=True
        )
        self.observer.start()
        logger.info("Hot reload enabled for prompt templates")

    def render(self, template_name: str, **kwargs) -> str:
        """
        Render a prompt template with given parameters.

        Args:
            template_name: Name of the template to render
            **kwargs: Parameters to pass to the template

        Returns:
            Rendered prompt string
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template_info = self.templates[template_name]
        template_str = template_info['template']

        # Create Jinja2 template
        template = self.jinja_env.from_string(template_str)

        # Add conversation context
        kwargs['conversation_context'] = self.conversation_context
        kwargs['current_context'] = self.context

        # Render
        try:
            rendered = template.render(**kwargs)

            # Record in conversation context
            self.conversation_context.append({
                'template': template_name,
                'parameters': kwargs.copy(),
                'rendered': rendered[:500]  # Store preview
            })

            return rendered

        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {e}")
            raise

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        return self.templates[template_name].copy()

    def list_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())

    def set_context(self, context: str):
        """
        Change the current context.

        Args:
            context: New context (exploration, analysis, validation)
        """
        self.context = context
        logger.info(f"Context changed to: {context}")

    def clear_conversation_context(self):
        """Clear accumulated conversation context."""
        self.conversation_context = []
        logger.debug("Conversation context cleared")

    def add_to_context(self, key: str, value: Any):
        """
        Add information to conversation context.

        Args:
            key: Context key
            value: Context value
        """
        self.conversation_context.append({
            'type': 'context_addition',
            'key': key,
            'value': value
        })

    def override_template(self, template_name: str, new_template: str):
        """
        Override a template at runtime.

        Args:
            template_name: Name of template to override
            new_template: New template string
        """
        self.templates[template_name] = {
            'template': new_template,
            'description': 'Runtime override',
            'parameters': [],
            'file_path': 'runtime'
        }
        logger.info(f"Template '{template_name}' overridden at runtime")

    def validate_parameters(self, template_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate that required parameters are provided.

        Args:
            template_name: Template to validate for
            parameters: Provided parameters

        Returns:
            True if all required parameters are present
        """
        if template_name not in self.templates:
            return False

        required_params = self.templates[template_name].get('parameters', [])
        for param in required_params:
            if param not in parameters:
                logger.warning(f"Missing required parameter '{param}' for template '{template_name}'")
                return False

        return True

    def __del__(self):
        """Cleanup observer on deletion."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()


# Auto-generated methods for common templates
class FinancialPromptFactory(PromptFactory):
    """
    Extended factory with convenience methods for financial analysis prompts.
    """

    def identify_report_type(
        self,
        file_name: str,
        headers: List[Dict],
        sample_rows: List[Dict],
        shape: Dict[str, Any]
    ) -> str:
        """Render report identification prompt."""
        return self.render(
            'identify_report_type',
            file_name=file_name,
            headers=headers,
            sample_rows=sample_rows,
            shape=shape
        )

    def classify_columns(
        self,
        report_type: str,
        columns: List[Dict],
        header_row: List[Any]
    ) -> str:
        """Render column classification prompt."""
        return self.render(
            'classify_columns',
            report_type=report_type,
            columns=columns,
            header_row=header_row
        )

    def validate_investment_calculation(
        self,
        account_name: str,
        account_name_english: str,
        monthly_values: Dict[str, float],
        row_number: int,
        monthly_revenue: float,
        restaurant_name: str
    ) -> str:
        """Render investment validation prompt."""
        return self.render(
            'validate_investment_calculation',
            account_name=account_name,
            account_name_english=account_name_english,
            monthly_values=monthly_values,
            row_number=row_number,
            monthly_revenue=monthly_revenue,
            restaurant_name=restaurant_name
        )