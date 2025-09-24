"""
Test suite for Enhanced Account Hierarchy Parser following TDD methodology.

These tests define the exact behavior required for fixing double counting issues
and integrating with the ValidationStateManager.
"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
from typing import Dict, Any, List

from src.parsers.account_hierarchy_parser import AccountHierarchyParser
from src.mcp_server.validation_state import ValidationStateManager


class TestEnhancedDoubleCountingPrevention:
    """Test enhanced double counting prevention logic."""

    def setup_method(self):
        """Setup parser and validation manager for each test."""
        self.parser = AccountHierarchyParser()
        self.validation_manager = ValidationStateManager()

    def test_identify_safe_accounts_conservative_approach(self):
        """Test that parser is conservative about excluding parent accounts."""
        # Create test data with clear parent-child relationships
        accounts = [
            {
                "name": "九、长期待摊费用",
                "clean_name": "长期待摊费用",
                "level": 1,
                "total_value": 100000,
                "is_numeric": True,
                "children": ["设施设备", "新店装修", "新店开办"]
            },
            {
                "name": "  设施设备",
                "clean_name": "设施设备",
                "level": 2,
                "total_value": 30000,
                "is_numeric": True,
                "children": []
            },
            {
                "name": "  新店装修",
                "clean_name": "新店装修",
                "level": 2,
                "total_value": 40000,
                "is_numeric": True,
                "children": []
            },
            {
                "name": "  新店开办",
                "clean_name": "新店开办",
                "level": 2,
                "total_value": 30000,
                "is_numeric": True,
                "children": []
            }
        ]

        # Build hierarchy tree
        hierarchy_tree = {}
        for account in accounts:
            hierarchy_tree[account["name"]] = account

        # Test conservative safe account identification
        safe_accounts = self.parser._identify_safe_accounts_conservative(hierarchy_tree)

        # Should only include leaf accounts (children), not parent
        assert "  设施设备" in safe_accounts
        assert "  新店装修" in safe_accounts
        assert "  新店开办" in safe_accounts
        assert "九、长期待摊费用" not in safe_accounts

    def test_detect_sum_validation_mismatches(self):
        """Test detection of parent-child sum mismatches."""
        # Create hierarchy with intentional mismatch
        hierarchy_tree = {
            "总收入": {
                "name": "总收入",
                "total_value": 100000,  # Parent value
                "is_numeric": True,
                "children": ["食品收入", "酒水收入"]
            },
            "食品收入": {
                "name": "食品收入",
                "total_value": 70000,
                "is_numeric": True,
                "children": []
            },
            "酒水收入": {
                "name": "酒水收入",
                "total_value": 25000,  # 70000 + 25000 = 95000 != 100000
                "is_numeric": True,
                "children": []
            }
        }

        validation_flags = self.parser._validate_hierarchy_enhanced(hierarchy_tree)

        # Should detect the 5000 difference
        assert len(validation_flags["sum_mismatches"]) == 1
        mismatch = validation_flags["sum_mismatches"][0]
        assert mismatch["parent"] == "总收入"
        assert mismatch["expected_total"] == 100000
        assert mismatch["children_total"] == 95000
        assert mismatch["difference"] == 5000

    def test_flag_ambiguous_accounts(self):
        """Test flagging of accounts with ambiguous parent-child status."""
        hierarchy_tree = {
            "营业费用": {
                "name": "营业费用",
                "total_value": 50000,  # Has value AND children - ambiguous!
                "is_numeric": True,
                "children": ["人工成本", "租金费用"]
            },
            "人工成本": {
                "name": "人工成本",
                "total_value": 30000,
                "is_numeric": True,
                "children": []
            },
            "租金费用": {
                "name": "租金费用",
                "total_value": 20000,
                "is_numeric": True,
                "children": []
            }
        }

        validation_flags = self.parser._validate_hierarchy_enhanced(hierarchy_tree)

        # Should flag ambiguous account
        assert len(validation_flags["ambiguous_accounts"]) == 1
        ambiguous = validation_flags["ambiguous_accounts"][0]
        assert ambiguous["account"] == "营业费用"
        assert "PARENT+VALUE" in ambiguous["warning"]

    def test_zero_value_accounts_handling(self):
        """Test proper handling of accounts with zero values."""
        hierarchy_tree = {
            "未使用科目": {
                "name": "未使用科目",
                "total_value": 0,
                "is_numeric": True,
                "children": []
            },
            "正常收入": {
                "name": "正常收入",
                "total_value": 50000,
                "is_numeric": True,
                "children": []
            }
        }

        safe_accounts = self.parser._identify_safe_accounts_conservative(hierarchy_tree)

        # Should exclude zero-value accounts by default
        assert "未使用科目" not in safe_accounts
        assert "正常收入" in safe_accounts

    def test_deep_hierarchy_handling(self):
        """Test handling of deep hierarchical structures."""
        hierarchy_tree = {
            "Level 1": {
                "name": "Level 1",
                "total_value": 100,
                "is_numeric": True,
                "children": ["Level 2"]
            },
            "Level 2": {
                "name": "Level 2",
                "total_value": 100,
                "is_numeric": True,
                "children": ["Level 3"]
            },
            "Level 3": {
                "name": "Level 3",
                "total_value": 100,
                "is_numeric": True,
                "children": ["Level 4"]
            },
            "Level 4": {
                "name": "Level 4",
                "total_value": 100,
                "is_numeric": True,
                "children": []  # Only this should be safe
            }
        }

        safe_accounts = self.parser._identify_safe_accounts_conservative(hierarchy_tree)

        # Only the deepest level should be safe
        assert safe_accounts == ["Level 4"]


class TestValidationStateIntegration:
    """Test integration with ValidationStateManager."""

    def setup_method(self):
        """Setup parser and validation manager for each test."""
        self.parser = AccountHierarchyParser()
        self.validation_manager = ValidationStateManager()

    def test_parse_with_validation_session(self):
        """Test parsing that creates and uses validation session."""
        file_path = "/test/restaurant_data.xlsx"

        # Mock the Excel parsing
        with patch('pandas.read_excel') as mock_read_excel:
            mock_df = pd.DataFrame({
                '项目': ['营业收入', '食品成本', '人工成本'],
                '2024年5月': [100000, 30000, 25000],
                '2024年6月': [110000, 33000, 27000]
            })
            mock_read_excel.return_value = mock_df

            # Parse with validation session
            result = self.parser.parse_hierarchy_with_validation(
                file_path,
                self.validation_manager
            )

            assert result["parsing_status"] == "success"
            assert "session_id" in result
            assert "validation_session" in result

            # Check that session was created
            session = self.validation_manager.get_session_for_file(file_path)
            assert session is not None
            assert session.file_path == file_path

    def test_conservative_recommendation_generation(self):
        """Test generation of conservative calculation recommendations."""
        hierarchy_result = {
            "hierarchy_tree": {
                "收入": {
                    "name": "收入",
                    "total_value": 100000,
                    "is_numeric": True,
                    "children": ["食品收入"]
                },
                "食品收入": {
                    "name": "食品收入",
                    "total_value": 100000,
                    "is_numeric": True,
                    "children": []
                }
            },
            "safe_accounts": ["食品收入"],
            "validation_flags": {
                "ambiguous_accounts": [
                    {"account": "收入", "warning": "Parent has value and children"}
                ]
            }
        }

        recommendations = self.parser._generate_conservative_recommendations(hierarchy_result)

        assert "use_leaf_accounts_only" in recommendations
        assert "exclude_ambiguous_accounts" in recommendations
        assert len(recommendations["excluded_accounts"]) > 0
        assert recommendations["recommended_accounts"] == ["食品收入"]

    def test_validation_report_generation(self):
        """Test generation of comprehensive validation reports."""
        hierarchy_result = {
            "total_accounts": 10,
            "safe_accounts": ["Account A", "Account B"],
            "validation_flags": {
                "sum_mismatches": [{"parent": "Parent X", "difference": 1000}],
                "ambiguous_accounts": [{"account": "Account Y", "warning": "Ambiguous"}]
            }
        }

        report = self.parser.generate_validation_report_enhanced(hierarchy_result)

        assert "Account Structure Analysis" in report
        assert "Safe Accounts (2)" in report
        assert "Sum Mismatches (1)" in report
        assert "Ambiguous Accounts (1)" in report
        assert "VALIDATION REQUIRED" in report


class TestDoubleCountingScenarios:
    """Test specific double counting scenarios from real data."""

    def setup_method(self):
        """Setup parser for each test."""
        self.parser = AccountHierarchyParser()

    def test_yebailian_scenario(self):
        """Test the specific Ye Bai Lian restaurant scenario that had double counting."""
        # Recreate the problematic hierarchy structure
        hierarchy_tree = {
            "九、长期待摊费用": {
                "name": "九、长期待摊费用",
                "total_value": 74310,  # Parent total
                "is_numeric": True,
                "children": ["设施设备", "新店装修", "新店开办"]
            },
            "设施设备": {
                "name": "设施设备",
                "total_value": 4613,
                "is_numeric": True,
                "children": []
            },
            "新店装修": {
                "name": "新店装修",
                "total_value": 24684,
                "is_numeric": True,
                "children": []
            },
            "新店开办": {
                "name": "新店开办",
                "total_value": 26543,
                "is_numeric": True,
                "children": []
            }
        }

        safe_accounts = self.parser._identify_safe_accounts_conservative(hierarchy_tree)
        validation_flags = self.parser._validate_hierarchy_enhanced(hierarchy_tree)

        # Should identify children as safe, parent as unsafe
        expected_safe = ["设施设备", "新店装修", "新店开办"]
        # The actual account names might have different formatting
        for expected in expected_safe:
            assert any(expected in safe_account for safe_account in safe_accounts), f"Expected {expected} to be in safe accounts"
        assert "九、长期待摊费用" not in safe_accounts

        # Should detect potential double counting risk
        assert len(validation_flags["ambiguous_accounts"]) >= 1

        # Should suggest using only leaf accounts
        recommendations = self.parser._generate_conservative_recommendations({
            "hierarchy_tree": hierarchy_tree,
            "safe_accounts": safe_accounts,
            "validation_flags": validation_flags
        })

        assert len(recommendations["recommended_accounts"]) == 3
        assert "九、长期待摊费用" in recommendations["excluded_accounts"]

    def test_multiple_parent_child_levels(self):
        """Test complex multi-level parent-child relationships."""
        hierarchy_tree = {
            "总成本": {
                "name": "总成本",
                "total_value": 200000,
                "is_numeric": True,
                "children": ["直接成本", "间接成本"]
            },
            "直接成本": {
                "name": "直接成本",
                "total_value": 150000,
                "is_numeric": True,
                "children": ["食品成本", "人工成本"]
            },
            "食品成本": {
                "name": "食品成本",
                "total_value": 100000,
                "is_numeric": True,
                "children": []
            },
            "人工成本": {
                "name": "人工成本",
                "total_value": 50000,
                "is_numeric": True,
                "children": []
            },
            "间接成本": {
                "name": "间接成本",
                "total_value": 50000,
                "is_numeric": True,
                "children": []
            }
        }

        safe_accounts = self.parser._identify_safe_accounts_conservative(hierarchy_tree)

        # Should only include leaf accounts
        expected_safe = ["食品成本", "人工成本", "间接成本"]
        assert all(account in safe_accounts for account in expected_safe)
        assert "总成本" not in safe_accounts
        assert "直接成本" not in safe_accounts


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases."""

    def setup_method(self):
        """Setup parser for each test."""
        self.parser = AccountHierarchyParser()

    def test_large_hierarchy_performance(self):
        """Test performance with large hierarchies."""
        # Create large hierarchy (100 accounts)
        hierarchy_tree = {}
        for i in range(100):
            account_name = f"账户_{i:03d}"
            hierarchy_tree[account_name] = {
                "name": account_name,
                "total_value": 1000 + i,
                "is_numeric": True,
                "children": [] if i > 50 else [f"账户_{i+50:03d}"] if i+50 < 100 else []
            }

        # Should complete in reasonable time
        import time
        start_time = time.time()
        safe_accounts = self.parser._identify_safe_accounts_conservative(hierarchy_tree)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 1.0  # Should complete in under 1 second
        assert len(safe_accounts) > 0

    def test_empty_hierarchy(self):
        """Test handling of empty hierarchy."""
        hierarchy_tree = {}

        safe_accounts = self.parser._identify_safe_accounts_conservative(hierarchy_tree)
        validation_flags = self.parser._validate_hierarchy_enhanced(hierarchy_tree)

        assert safe_accounts == []
        assert validation_flags["sum_mismatches"] == []
        assert validation_flags["ambiguous_accounts"] == []

    def test_circular_reference_detection(self):
        """Test detection of circular references in hierarchy."""
        # This would be malformed data, but we should handle it gracefully
        hierarchy_tree = {
            "A": {
                "name": "A",
                "total_value": 100,
                "is_numeric": True,
                "children": ["B"]
            },
            "B": {
                "name": "B",
                "total_value": 50,
                "is_numeric": True,
                "children": ["A"]  # Circular reference!
            }
        }

        # Should not crash and should flag as problematic
        validation_flags = self.parser._validate_hierarchy_enhanced(hierarchy_tree)

        # Should be flagged in validation results
        assert len(validation_flags.get("circular_references", [])) > 0 or \
               len(validation_flags.get("ambiguous_accounts", [])) > 0


class TestIntegrationWorkflow:
    """Test complete integration workflow."""

    def setup_method(self):
        """Setup components for integration tests."""
        self.parser = AccountHierarchyParser()
        self.validation_manager = ValidationStateManager()

    def test_full_validation_workflow(self):
        """Test complete workflow from parsing to validation confirmation."""
        file_path = "/test/integration_test.xlsx"

        # Mock Excel data
        with patch('pandas.read_excel') as mock_read_excel:
            mock_df = pd.DataFrame({
                '科目': ['营业收入', '食品收入', '酒水收入', '营业成本', '食品成本'],
                '金额': [200000, 150000, 50000, 120000, 100000]
            })
            mock_read_excel.return_value = mock_df

            # Step 1: Parse with validation
            result = self.parser.parse_hierarchy_with_validation(
                file_path,
                self.validation_manager
            )

            assert result["parsing_status"] == "success"
            session_id = result["session_id"]

            # Step 2: Confirm account structure
            self.validation_manager.confirm_account_structure(
                session_id,
                result
            )

            # Step 3: Check calculation readiness
            can_proceed, missing = self.validation_manager.can_proceed_with_calculation(file_path)

            # Should still need other confirmations
            assert can_proceed is False
            assert "Depreciation periods not confirmed" in missing

            # Step 4: Complete all validations
            self.validation_manager.confirm_depreciation_periods(session_id, {"装修": 3})
            self.validation_manager.confirm_safe_accounts(session_id, result["safe_accounts"])
            self.validation_manager.confirm_benchmark_preferences(session_id, {"food_cost": 0.30})

            # Step 5: Should now be ready for calculation
            can_proceed, missing = self.validation_manager.can_proceed_with_calculation(file_path)
            assert can_proceed is True
            assert missing == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])