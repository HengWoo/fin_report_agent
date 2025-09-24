"""
Simple Data Extraction Tools

Pure data extraction utilities with NO business logic or accounting rules.
These tools simply extract raw data from Excel files for Claude to analyze.
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class SimpleDataExtractor:
    """
    Pure data extraction from Excel files.
    No interpretation, no accounting logic, just raw data access.
    """

    def __init__(self):
        """Initialize the extractor."""
        self._cached_df = None
        self._cached_file = None

    def _load_excel(self, file_path: str, use_cache: bool = True) -> pd.DataFrame:
        """
        Load Excel file with caching support.

        Args:
            file_path: Path to Excel file
            use_cache: Whether to use cached DataFrame if available

        Returns:
            DataFrame with raw Excel data
        """
        file_path = str(Path(file_path).resolve())

        if use_cache and self._cached_file == file_path and self._cached_df is not None:
            return self._cached_df

        # Load without any header interpretation
        df = pd.read_excel(file_path, header=None)

        if use_cache:
            self._cached_df = df
            self._cached_file = file_path

        return df

    def get_excel_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic structure information about the Excel file.

        Args:
            file_path: Path to Excel file

        Returns:
            Dictionary containing:
            - shape: (rows, columns)
            - headers: First few rows that might contain headers
            - sample_rows: Sample data rows
            - all_sheets: List of sheet names if multiple
        """
        # Get all sheet names
        xl_file = pd.ExcelFile(file_path)
        all_sheets = xl_file.sheet_names

        # Load first sheet
        df = self._load_excel(file_path)

        structure = {
            "shape": df.shape,
            "total_rows": df.shape[0],
            "total_columns": df.shape[1],
            "all_sheets": all_sheets,
            "active_sheet": all_sheets[0] if all_sheets else None,
            "headers": [],
            "sample_rows": [],
            "column_samples": {}
        }

        # Get potential header rows (first 5 rows)
        for i in range(min(5, len(df))):
            row_data = df.iloc[i].tolist()
            structure["headers"].append({
                "row_index": i,
                "values": row_data,
                "non_null_count": sum(1 for v in row_data if pd.notna(v))
            })

        # Get sample data rows (rows 5-10)
        for i in range(5, min(10, len(df))):
            row_data = df.iloc[i].tolist()
            structure["sample_rows"].append({
                "row_index": i,
                "values": row_data,
                "non_null_count": sum(1 for v in row_data if pd.notna(v))
            })

        # Get column samples (5 values from each column)
        for col_idx in range(df.shape[1]):
            col_data = df.iloc[:, col_idx]
            non_null = col_data[col_data.notna()]
            samples = non_null.head(5).tolist() if len(non_null) > 0 else []
            structure["column_samples"][col_idx] = {
                "samples": samples,
                "non_null_count": len(non_null),
                "data_types": self._detect_column_types(col_data)
            }

        return structure

    def _detect_column_types(self, series: pd.Series) -> List[str]:
        """
        Detect possible data types in a column.

        Args:
            series: Pandas Series to analyze

        Returns:
            List of detected types (numeric, text, date, etc.)
        """
        types = []
        non_null = series[series.notna()]

        if len(non_null) == 0:
            return ["empty"]

        # Check for numeric
        try:
            pd.to_numeric(non_null)
            types.append("numeric")
        except:
            pass

        # Check for dates
        try:
            pd.to_datetime(non_null)
            types.append("date")
        except:
            pass

        # Check for text
        if non_null.apply(lambda x: isinstance(x, str)).any():
            types.append("text")

        # Check for boolean-like
        unique_vals = non_null.unique()
        if len(unique_vals) <= 2:
            types.append("boolean-like")

        return types if types else ["unknown"]

    def get_cell_value(self, file_path: str, row: int, col: int) -> Any:
        """
        Get a single cell value.

        Args:
            file_path: Path to Excel file
            row: Row index (0-based)
            col: Column index (0-based)

        Returns:
            Cell value or None if out of bounds
        """
        df = self._load_excel(file_path)

        if row >= len(df) or col >= len(df.columns):
            return None

        return df.iloc[row, col]

    def get_row(self, file_path: str, row_index: int) -> List[Any]:
        """
        Get entire row as list.

        Args:
            file_path: Path to Excel file
            row_index: Row index (0-based)

        Returns:
            List of values in the row
        """
        df = self._load_excel(file_path)

        if row_index >= len(df):
            return []

        return df.iloc[row_index].tolist()

    def get_column(self, file_path: str, col_index: int) -> List[Any]:
        """
        Get entire column as list.

        Args:
            file_path: Path to Excel file
            col_index: Column index (0-based)

        Returns:
            List of values in the column
        """
        df = self._load_excel(file_path)

        if col_index >= len(df.columns):
            return []

        return df.iloc[:, col_index].tolist()

    def get_range(
        self,
        file_path: str,
        start_row: int,
        end_row: int,
        start_col: Optional[int] = None,
        end_col: Optional[int] = None
    ) -> List[List[Any]]:
        """
        Get a range of data.

        Args:
            file_path: Path to Excel file
            start_row: Starting row index (inclusive)
            end_row: Ending row index (exclusive)
            start_col: Starting column index (inclusive), None for all columns
            end_col: Ending column index (exclusive), None for all columns

        Returns:
            2D list of values
        """
        df = self._load_excel(file_path)

        # Handle None values for columns
        if start_col is None:
            start_col = 0
        if end_col is None:
            end_col = len(df.columns)

        # Ensure bounds
        start_row = max(0, start_row)
        end_row = min(len(df), end_row)
        start_col = max(0, start_col)
        end_col = min(len(df.columns), end_col)

        # Extract range
        range_df = df.iloc[start_row:end_row, start_col:end_col]

        return range_df.values.tolist()

    def find_non_empty_columns(self, file_path: str, row_index: int) -> List[int]:
        """
        Find columns that have non-empty values in a specific row.

        Args:
            file_path: Path to Excel file
            row_index: Row to examine

        Returns:
            List of column indices with non-empty values
        """
        row_data = self.get_row(file_path, row_index)

        non_empty = []
        for idx, value in enumerate(row_data):
            if pd.notna(value) and str(value).strip() != "":
                non_empty.append(idx)

        return non_empty

    def search_value(self, file_path: str, search_value: Any) -> List[Tuple[int, int]]:
        """
        Search for a value in the Excel file.

        Args:
            file_path: Path to Excel file
            search_value: Value to search for

        Returns:
            List of (row, col) tuples where value is found
        """
        df = self._load_excel(file_path)
        locations = []

        for row_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                cell_value = df.iloc[row_idx, col_idx]
                if pd.notna(cell_value) and str(cell_value) == str(search_value):
                    locations.append((row_idx, col_idx))

        return locations

    def get_numeric_columns(self, file_path: str, sample_rows: int = 10) -> List[int]:
        """
        Identify columns that appear to contain numeric data.

        Args:
            file_path: Path to Excel file
            sample_rows: Number of rows to sample for detection

        Returns:
            List of column indices that contain numeric data
        """
        df = self._load_excel(file_path)
        numeric_cols = []

        # Skip first few rows (likely headers)
        start_row = min(5, len(df) - sample_rows)
        sample_df = df.iloc[start_row:start_row + sample_rows]

        for col_idx in range(len(df.columns)):
            col_sample = sample_df.iloc[:, col_idx]
            non_null = col_sample[col_sample.notna()]

            if len(non_null) > 0:
                try:
                    # Try to convert to numeric
                    pd.to_numeric(non_null)
                    numeric_cols.append(col_idx)
                except:
                    pass

        return numeric_cols

    def get_text_columns(self, file_path: str, sample_rows: int = 10) -> List[int]:
        """
        Identify columns that appear to contain text data.

        Args:
            file_path: Path to Excel file
            sample_rows: Number of rows to sample for detection

        Returns:
            List of column indices that contain text data
        """
        df = self._load_excel(file_path)
        text_cols = []

        # Skip first few rows (likely headers)
        start_row = min(5, len(df) - sample_rows)
        sample_df = df.iloc[start_row:start_row + sample_rows]

        for col_idx in range(len(df.columns)):
            col_sample = sample_df.iloc[:, col_idx]
            non_null = col_sample[col_sample.notna()]

            if len(non_null) > 0:
                # Check if any values are strings
                if non_null.apply(lambda x: isinstance(x, str)).any():
                    # And cannot be converted to pure numeric
                    try:
                        pd.to_numeric(non_null)
                    except:
                        text_cols.append(col_idx)

        return text_cols