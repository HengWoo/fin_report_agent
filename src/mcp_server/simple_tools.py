"""
Simple Tools for Claude-Driven Intelligence

Philosophy: Tools don't think, Claude thinks.
- Tools extract/calculate, never interpret
- Tools return raw data, never make decisions
- All intelligence lives in Claude's reasoning

These 5 tools are sufficient for Claude to:
- Parse any Excel file
- Verify results
- Make intelligent decisions
- Explain everything to users
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
from pathlib import Path


def read_excel_region(
    file_path: str, start_row: int, end_row: int, start_col: int, end_col: int
) -> List[List[Any]]:
    """
    Extract a rectangular region of cells from Excel.

    No interpretation, just raw data extraction.

    Args:
        file_path: Path to Excel file
        start_row: Starting row (0-indexed)
        end_row: Ending row (inclusive)
        start_col: Starting column (0-indexed)
        end_col: Ending column (inclusive)

    Returns:
        2D list of cell values

    Example:
        read_excel_region("report.xlsx", 120, 125, 0, 5)
        # Returns 6 rows x 6 columns of raw data
    """
    df = pd.read_excel(file_path, header=None)
    region = df.iloc[start_row : end_row + 1, start_col : end_col + 1]
    return region.values.tolist()


def search_in_excel(
    file_path: str, search_term: str, case_sensitive: bool = False
) -> List[Tuple[int, int, Any]]:
    """
    Find all cells containing a search term.

    No interpretation of what the match means.

    Args:
        file_path: Path to Excel file
        search_term: Text to search for
        case_sensitive: Whether to match case

    Returns:
        List of (row, col, value) tuples where matches found

    Example:
        search_in_excel("report.xlsx", "长期待摊费用")
        # Returns: [(122, 0, "九、长期待摊费用")]
    """
    df = pd.read_excel(file_path, header=None)
    matches = []

    for row in range(len(df)):
        for col in range(len(df.columns)):
            cell_value = df.iloc[row, col]
            cell_str = str(cell_value) if pd.notna(cell_value) else ""

            # Search logic
            if case_sensitive:
                if search_term in cell_str:
                    matches.append((row, col, cell_value))
            else:
                if search_term.lower() in cell_str.lower():
                    matches.append((row, col, cell_value))

    return matches


def get_excel_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic information about Excel file structure.

    No interpretation, just dimensions and metadata.

    Args:
        file_path: Path to Excel file

    Returns:
        Dictionary with basic file info

    Example:
        get_excel_info("report.xlsx")
        # Returns: {"rows": 150, "columns": 28, "sheets": ["损益表"]}
    """
    excel_file = pd.ExcelFile(file_path)

    # Read first sheet to get dimensions
    df = pd.read_excel(file_path, header=None)

    return {
        "file_path": str(Path(file_path).name),
        "rows": len(df),
        "columns": len(df.columns),
        "sheets": excel_file.sheet_names,
        "file_size_bytes": Path(file_path).stat().st_size,
    }


def calculate(operation: str, values: List[float]) -> float:
    """
    Perform simple mathematical operations.

    Claude decides what to calculate, tool just does the math.

    Args:
        operation: One of "sum", "average", "max", "min"
        values: List of numbers to operate on

    Returns:
        Calculated result

    Example:
        calculate("sum", [23537.98, 24603.14, 25764.89])
        # Returns: 73906.01
    """
    if not values:
        return 0.0

    # Filter out None values
    clean_values = [v for v in values if v is not None]

    if not clean_values:
        return 0.0

    if operation == "sum":
        return sum(clean_values)
    elif operation == "average":
        return sum(clean_values) / len(clean_values)
    elif operation == "max":
        return max(clean_values)
    elif operation == "min":
        return min(clean_values)
    else:
        raise ValueError(
            f"Unknown operation: {operation}. Use sum, average, max, or min"
        )


def show_excel_visual(file_path: str, max_rows: int = 20, max_cols: int = 10) -> str:
    """
    Display Excel in a format Claude can read and understand.

    Shows raw data with row/column labels for reference.

    Args:
        file_path: Path to Excel file
        max_rows: Maximum rows to show
        max_cols: Maximum columns to show

    Returns:
        Formatted string representation of Excel data

    Example:
        show_excel_visual("report.xlsx", 10, 5)
        # Returns readable table with first 10 rows, 5 columns
    """
    df = pd.read_excel(file_path, header=None)

    # Limit dimensions
    display_df = df.iloc[:max_rows, :max_cols].copy()

    # Add row labels
    display_df.index = [f"Row {i}" for i in range(len(display_df))]

    # Add column labels
    display_df.columns = [f"Col {i}" for i in range(len(display_df.columns))]

    # Format as string
    output = f"Excel File: {Path(file_path).name}\n"
    output += (
        f"Showing first {len(display_df)} rows, {len(display_df.columns)} columns\n"
    )
    output += "=" * 80 + "\n"
    output += display_df.to_string()

    if len(df) > max_rows or len(df.columns) > max_cols:
        output += f"\n\n... ({len(df)} total rows, {len(df.columns)} total columns)"

    return output


# Simple tool metadata for MCP registration
SIMPLE_TOOLS = {
    "read_excel_region": {
        "description": "Extract a rectangular region of cells from Excel. Returns raw data with no interpretation.",
        "parameters": {
            "file_path": "Path to Excel file",
            "start_row": "Starting row (0-indexed)",
            "end_row": "Ending row (inclusive)",
            "start_col": "Starting column (0-indexed)",
            "end_col": "Ending column (inclusive)",
        },
    },
    "search_in_excel": {
        "description": "Find all cells containing a search term. Returns locations and values.",
        "parameters": {
            "file_path": "Path to Excel file",
            "search_term": "Text to search for",
            "case_sensitive": "Whether to match case (optional, default False)",
        },
    },
    "get_excel_info": {
        "description": "Get basic Excel file structure: rows, columns, sheet names.",
        "parameters": {"file_path": "Path to Excel file"},
    },
    "calculate": {
        "description": "Perform simple math: sum, average, max, min. Claude decides what to calculate.",
        "parameters": {
            "operation": "One of: sum, average, max, min",
            "values": "List of numbers to operate on",
        },
    },
    "show_excel_visual": {
        "description": "Display Excel in readable format for Claude to analyze. Shows raw data with labels.",
        "parameters": {
            "file_path": "Path to Excel file",
            "max_rows": "Maximum rows to show (optional, default 20)",
            "max_cols": "Maximum columns to show (optional, default 10)",
        },
    },
}
