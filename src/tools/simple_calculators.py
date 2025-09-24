"""
Simple Calculation Tools

Pure mathematical operations with NO accounting rules or business logic.
These tools perform calculations as directed by Claude's analysis.
"""

from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np


class SimpleCalculator:
    """
    Pure mathematical operations without any business logic.
    All accounting intelligence comes from Claude's instructions.
    """

    def sum_values(self, values: List[Union[float, int]]) -> float:
        """
        Sum a list of numeric values, ignoring non-numeric entries.

        Args:
            values: List of values to sum

        Returns:
            Sum of numeric values
        """
        numeric_values = []
        for val in values:
            try:
                if pd.notna(val):
                    numeric_values.append(float(val))
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue

        return sum(numeric_values)

    def sum_columns(
        self,
        data: List[List[Any]],
        column_indices: List[int]
    ) -> List[float]:
        """
        Sum specified columns for each row.

        Args:
            data: 2D list of data
            column_indices: Which columns to sum (0-based)

        Returns:
            List of sums for each row
        """
        row_sums = []

        for row in data:
            row_sum = 0.0
            for col_idx in column_indices:
                if col_idx < len(row):
                    try:
                        if pd.notna(row[col_idx]):
                            row_sum += float(row[col_idx])
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        continue
            row_sums.append(row_sum)

        return row_sums

    def sum_rows(
        self,
        data: List[List[Any]],
        row_indices: List[int]
    ) -> List[float]:
        """
        Sum specified rows for each column.

        Args:
            data: 2D list of data
            row_indices: Which rows to sum (0-based)

        Returns:
            List of sums for each column
        """
        if not data or not row_indices:
            return []

        num_cols = len(data[0]) if data else 0
        col_sums = [0.0] * num_cols

        for row_idx in row_indices:
            if row_idx < len(data):
                row = data[row_idx]
                for col_idx in range(min(len(row), num_cols)):
                    try:
                        if pd.notna(row[col_idx]):
                            col_sums[col_idx] += float(row[col_idx])
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        continue

        return col_sums

    def calculate_ratio(
        self,
        numerator: float,
        denominator: float,
        as_percentage: bool = True
    ) -> Optional[float]:
        """
        Calculate ratio or percentage.

        Args:
            numerator: Top value
            denominator: Bottom value
            as_percentage: Return as percentage (0-100) or ratio (0-1)

        Returns:
            Ratio/percentage or None if denominator is 0
        """
        try:
            numerator = float(numerator)
            denominator = float(denominator)

            if abs(denominator) < 1e-10:  # Avoid division by zero
                return None

            ratio = numerator / denominator
            return ratio * 100 if as_percentage else ratio

        except (ValueError, TypeError):
            return None

    def multiply(self, value: float, factor: float) -> float:
        """
        Simple multiplication.

        Args:
            value: Base value
            factor: Multiplication factor

        Returns:
            Product
        """
        try:
            return float(value) * float(factor)
        except (ValueError, TypeError):
            return 0.0

    def average(self, values: List[Union[float, int]]) -> Optional[float]:
        """
        Calculate average of numeric values.

        Args:
            values: List of values

        Returns:
            Average or None if no numeric values
        """
        numeric_values = []
        for val in values:
            try:
                if pd.notna(val):
                    numeric_values.append(float(val))
            except (ValueError, TypeError):
                continue

        if not numeric_values:
            return None

        return sum(numeric_values) / len(numeric_values)

    def find_max(self, values: List[Union[float, int]]) -> Optional[float]:
        """
        Find maximum value.

        Args:
            values: List of values

        Returns:
            Maximum value or None if no numeric values
        """
        numeric_values = []
        for val in values:
            try:
                if pd.notna(val):
                    numeric_values.append(float(val))
            except (ValueError, TypeError):
                continue

        return max(numeric_values) if numeric_values else None

    def find_min(self, values: List[Union[float, int]]) -> Optional[float]:
        """
        Find minimum value.

        Args:
            values: List of values

        Returns:
            Minimum value or None if no numeric values
        """
        numeric_values = []
        for val in values:
            try:
                if pd.notna(val):
                    numeric_values.append(float(val))
            except (ValueError, TypeError):
                continue

        return min(numeric_values) if numeric_values else None

    def calculate_growth_rate(
        self,
        old_value: float,
        new_value: float,
        as_percentage: bool = True
    ) -> Optional[float]:
        """
        Calculate growth rate between two values.

        Args:
            old_value: Starting value
            new_value: Ending value
            as_percentage: Return as percentage or decimal

        Returns:
            Growth rate or None if old_value is 0
        """
        try:
            old_value = float(old_value)
            new_value = float(new_value)

            if abs(old_value) < 1e-10:
                return None

            growth = (new_value - old_value) / old_value
            return growth * 100 if as_percentage else growth

        except (ValueError, TypeError):
            return None

    def calculate_cumulative_sum(self, values: List[Union[float, int]]) -> List[float]:
        """
        Calculate cumulative sum of values.

        Args:
            values: List of values

        Returns:
            List of cumulative sums
        """
        cumulative = []
        running_sum = 0.0

        for val in values:
            try:
                if pd.notna(val):
                    running_sum += float(val)
            except (ValueError, TypeError):
                # Keep previous sum if value is non-numeric
                pass
            cumulative.append(running_sum)

        return cumulative

    def calculate_moving_average(
        self,
        values: List[Union[float, int]],
        window: int
    ) -> List[Optional[float]]:
        """
        Calculate moving average.

        Args:
            values: List of values
            window: Window size for moving average

        Returns:
            List of moving averages (None for insufficient data points)
        """
        result = []
        numeric_values = []

        # Convert to numeric
        for val in values:
            try:
                if pd.notna(val):
                    numeric_values.append(float(val))
                else:
                    numeric_values.append(np.nan)
            except (ValueError, TypeError):
                numeric_values.append(np.nan)

        # Calculate moving average
        for i in range(len(numeric_values)):
            if i < window - 1:
                result.append(None)
            else:
                window_values = [
                    v for v in numeric_values[i - window + 1:i + 1]
                    if not np.isnan(v)
                ]
                if window_values:
                    result.append(sum(window_values) / len(window_values))
                else:
                    result.append(None)

        return result

    def round_values(
        self,
        values: List[Union[float, int]],
        decimal_places: int = 2
    ) -> List[float]:
        """
        Round numeric values to specified decimal places.

        Args:
            values: List of values to round
            decimal_places: Number of decimal places

        Returns:
            List of rounded values
        """
        rounded = []
        for val in values:
            try:
                if pd.notna(val):
                    rounded.append(round(float(val), decimal_places))
                else:
                    rounded.append(0.0)
            except (ValueError, TypeError):
                rounded.append(0.0)

        return rounded

    def filter_by_threshold(
        self,
        values: List[Union[float, int]],
        threshold: float,
        comparison: str = "greater"
    ) -> List[int]:
        """
        Find indices of values meeting threshold criteria.

        Args:
            values: List of values to filter
            threshold: Threshold value
            comparison: "greater", "less", "equal", "greater_equal", "less_equal"

        Returns:
            List of indices meeting criteria
        """
        indices = []

        for i, val in enumerate(values):
            try:
                if pd.notna(val):
                    val_float = float(val)

                    if comparison == "greater" and val_float > threshold:
                        indices.append(i)
                    elif comparison == "less" and val_float < threshold:
                        indices.append(i)
                    elif comparison == "equal" and abs(val_float - threshold) < 1e-10:
                        indices.append(i)
                    elif comparison == "greater_equal" and val_float >= threshold:
                        indices.append(i)
                    elif comparison == "less_equal" and val_float <= threshold:
                        indices.append(i)
            except (ValueError, TypeError):
                continue

        return indices

    def calculate_variance(self, values: List[Union[float, int]]) -> Optional[float]:
        """
        Calculate variance of numeric values.

        Args:
            values: List of values

        Returns:
            Variance or None if insufficient data
        """
        numeric_values = []
        for val in values:
            try:
                if pd.notna(val):
                    numeric_values.append(float(val))
            except (ValueError, TypeError):
                continue

        if len(numeric_values) < 2:
            return None

        mean = sum(numeric_values) / len(numeric_values)
        variance = sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)

        return variance

    def calculate_standard_deviation(
        self,
        values: List[Union[float, int]]
    ) -> Optional[float]:
        """
        Calculate standard deviation of numeric values.

        Args:
            values: List of values

        Returns:
            Standard deviation or None if insufficient data
        """
        variance = self.calculate_variance(values)
        return np.sqrt(variance) if variance is not None else None