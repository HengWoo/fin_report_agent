# Column Intelligence System

## Overview

The Column Intelligence System automatically analyzes Excel column headers to understand their purpose and make smart decisions about how to process financial data. This prevents common parsing errors like double counting, including non-financial data, and misinterpreting ratios as values.

## The Problem It Solves

### Before Column Intelligence ❌
```
九、长期待摊费用 calculation:
  Column 11 (5月): ¥23,537.98
+ Column 13 (6月): ¥24,603.14
+ Column 15 (7月): ¥25,764.89
+ Column 25 (合计): ¥73,906.01  ← Subtotal (already includes periods!)
+ Column 27 (备注): ¥50,368.04  ← Notes, not financial data!
= ¥198,180.28 ❌ WRONG (double counted + spurious data)
```

### After Column Intelligence ✅
```
九、长期待摊费用 calculation:
  Column 25 (合计): ¥73,906.01  ← Use subtotal directly
  (Excludes: Period columns, note columns, ratio columns)
= ¥73,906.01 ✅ CORRECT
```

## How It Works

### 1. Column Classification

The system classifies each column by analyzing its header:

| Column Type | Chinese Patterns | English Patterns | Action |
|------------|------------------|------------------|--------|
| **PERIOD** | 月, 季度, 年 | Jan, Q1, Quarter | ✅ Include in calculations |
| **VALUE** | (numeric data) | (numeric data) | ✅ Include in calculations |
| **SUBTOTAL** | 合计, 总计, 小计 | Total, Subtotal | ✅ Use for value, don't sum |
| **NOTE** | 备注, 说明, 附注 | Notes, Remark | ❌ Exclude completely |
| **RATIO** | 占比, 比例, % | Ratio, Percentage | ❌ Exclude completely |

### 2. Smart Value Extraction

```python
def extract_value(row_data, column_classifications):
    # Priority 1: Use subtotal if available (prevents double counting)
    for col in subtotal_columns:
        if has_value(row_data[col]):
            return row_data[col]  # Use subtotal, don't sum!

    # Priority 2: Sum only value/period columns
    total = 0
    for col in value_columns:
        if has_value(row_data[col]):
            total += row_data[col]

    return total
    # Note: Never includes note or ratio columns!
```

### 3. Validation

The system validates its decisions:
- Compares period sums against subtotal columns
- Flags variances as data quality issues
- Shows users exactly what was included/excluded

## When Column Intelligence Activates

### Activation Points

Column intelligence runs automatically in these scenarios:

#### 1. **MCP parse_excel Tool** (Primary Entry Point)
```
User → Claude → MCP "parse_excel" tool → Column Intelligence
```
- **When**: User asks Claude to analyze an Excel file
- **Example**: "帮我分析这份财务报表"
- **File**: `src/mcp_server/server.py::_handle_parse_excel()`
- **Status**: ✅ Active (as of latest update)

#### 2. **Orchestrator Validation Phase**
```
Orchestrator → Hierarchy Validation → parse_hierarchy() → Column Intelligence
```
- **When**: During mandatory validation before analysis
- **File**: `src/orchestration/claude_orchestrator.py::_phase_hierarchy_validation()`
- **Status**: ✅ Active

#### 3. **Direct Tool Calls**
```
validate_account_structure → parse_hierarchy() → Column Intelligence
```
- **When**: User explicitly validates account structure
- **File**: Various MCP tools
- **Status**: ✅ Active

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Request                            │
│  "Claude, analyze my restaurant financial report"          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   MCP parse_excel      │
         │   (Entry Point)        │
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────────────────┐
         │  AccountHierarchyParser            │
         │  .parse_hierarchy()                │
         └───────────┬────────────────────────┘
                     │
                     ▼
         ┌────────────────────────────────────┐
         │  ColumnClassifier                  │
         │  .classify_columns()               │
         └───────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────────┐
│ Detect:       │         │ Detect:          │
│ • 合计 cols   │         │ • 备注 cols      │
│ • Period cols │         │ • 占比 cols      │
└───────┬───────┘         └────────┬─────────┘
        │                          │
        └──────────┬───────────────┘
                   │
                   ▼
         ┌──────────────────────┐
         │ Smart Extraction     │
         │ • Use subtotals      │
         │ • Exclude notes      │
         │ • Exclude ratios     │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Return Results to    │
         │ Claude with:         │
         │ • Accurate values    │
         │ • Intelligence info  │
         │ • Quality score      │
         └──────────────────────┘
```

## Technical Implementation

### Core Components

#### 1. ColumnClassifier (`src/parsers/column_classifier.py`)
```python
class ColumnClassifier:
    def classify_columns(df: DataFrame) -> Dict[int, Dict]:
        """
        Analyze each column and determine its type.
        Handles both standard Excel and Chinese financial formats.
        """

    def _should_use_first_row_as_headers(df: DataFrame) -> bool:
        """
        Detect if first data row contains actual headers.
        Common in Chinese Excel files with generic column names.
        """
```

#### 2. AccountHierarchyParser (`src/parsers/account_hierarchy_parser.py`)
```python
class AccountHierarchyParser:
    def __init__(self):
        self.column_classifier = ColumnClassifier()

    def parse_hierarchy(file_path: str) -> Dict:
        """
        Parse with column intelligence:
        1. Classify all columns
        2. Extract using smart logic
        3. Return with intelligence metadata
        """
```

#### 3. MCP Integration (`src/mcp_server/server.py`)
```python
async def _handle_parse_excel(arguments: dict):
    """
    MCP tool that uses AccountHierarchyParser.
    Returns results with column intelligence to Claude.
    """
    hierarchy_result = self.hierarchy_parser.parse_hierarchy(file_path)
    # Returns: accounts, column_intelligence, validation info
```

### Data Flow

1. **Input**: Excel file with Chinese headers
2. **Classification**: Analyze headers (合计, 备注, 占比, etc.)
3. **Extraction**: Use subtotals when available, exclude notes/ratios
4. **Validation**: Cross-check with subtotals
5. **Output**: Accurate data + intelligence report

## Usage Examples

### For Developers

#### Using Column Intelligence Directly
```python
from src.parsers.account_hierarchy_parser import AccountHierarchyParser

parser = AccountHierarchyParser()
result = parser.parse_hierarchy("financial_report.xlsx")

# Access column intelligence
col_intel = result["column_intelligence"]
print(f"Value columns: {col_intel['value_columns']}")
print(f"Subtotal columns: {col_intel['subtotal_columns']}")
print(f"Excluded: {col_intel['excluded_columns']}")

# Access accounts with smart values
for account in result["accounts"]:
    if account["used_subtotal"]:
        print(f"{account['name']}: ¥{account['total_value']} (from subtotal)")
```

#### Getting Intelligence Report
```python
parser = AccountHierarchyParser()
result = parser.parse_hierarchy("report.xlsx")

# Generate human-readable report
report = parser.generate_column_intelligence_report(result)
print(report)
```

### For Claude/Users

Column intelligence works automatically when you use MCP tools:

```
User: "帮我分析这份财务报表 @report.xlsx"

Claude uses: parse_excel tool
↓
Response includes:
📊 Excel文件解析成功 (智能列识别)
🧠 列智能分析:
• 数值列: 12 个
• 小计列: 1 个 (用于值，不参与求和)
• 排除列: 16 个
  - 备注列: 1 个
  - 占比列: 13 个
```

## Configuration

### Pattern Customization

You can extend the patterns in `ColumnClassifier`:

```python
# Add new patterns
SUBTOTAL_PATTERNS = [
    '合计', '总计', '小计',  # Existing
    '累计', '汇总'           # Add custom
]

NOTE_PATTERNS = [
    '备注', '说明',          # Existing
    '附件', '补充说明'       # Add custom
]
```

### Tolerance Settings

```python
# In validate_with_subtotals()
tolerance_pct = 0.01  # 1% tolerance for subtotal variance
```

## Testing

### Run Column Intelligence Tests
```bash
# Basic functionality
uv run python test_column_intelligence.py

# MCP integration
uv run python test_mcp_column_intelligence.py

# Comprehensive validation
uv run python test_validation_claims.py
```

### Expected Results
- ✅ Subtotal columns detected (合计)
- ✅ Note columns excluded (备注)
- ✅ Ratio columns excluded (占比)
- ✅ Investment account: ¥73,906.01 (not ¥198,180.28)
- ✅ All accounts using subtotals marked

## Benefits

### 1. Prevents Double Counting
- Detects subtotal columns automatically
- Uses subtotals instead of summing periods + subtotals
- Saves ¥124,274.27 in the Ye Bai Lian case!

### 2. Excludes Irrelevant Data
- Notes/remarks columns ignored
- Ratio/percentage columns not treated as values
- Clean, accurate financial data only

### 3. Data Quality Insights
- Cross-validates with subtotals
- Flags data quality issues
- Provides transparency on decisions

### 4. Language Agnostic
- Handles Chinese and English patterns
- Detects headers in first row (Chinese format)
- Adapts to various Excel layouts

## Monitoring and Validation

### Check Intelligence Activation
```python
# In your code
if "column_intelligence" in hierarchy_result:
    print("✅ Column intelligence active")
    print(f"Data quality: {hierarchy_result['column_intelligence']['data_quality_score']}")
```

### Validation Reports
The system generates detailed reports showing:
- Which columns were classified and how
- Which values came from subtotals
- What was excluded and why
- Data quality scores

## Troubleshooting

### Issue: Subtotal Not Detected
**Symptom**: System sums all columns instead of using subtotal

**Solution**: Check pattern matching
```python
# The subtotal header must contain one of these:
SUBTOTAL_PATTERNS = ['合计', '总计', '小计', 'Total', 'Subtotal']

# Verify your Excel header matches
```

### Issue: Wrong Columns Excluded
**Symptom**: Important data excluded from calculations

**Solution**: Review classification report
```python
result = parser.parse_hierarchy(file_path)
print(result["column_intelligence"]["classification_report"])
# Check if classification is correct
```

### Issue: Headers Not Recognized
**Symptom**: All columns classified as "unknown"

**Solution**: Excel may have headers in first row
```python
# System auto-detects if >50% columns are "Unnamed:"
# Verify with:
df = pd.read_excel(file_path)
print(df.columns)  # Check for "Unnamed: X" pattern
```

## Future Enhancements

Planned improvements:
1. **ML-based classification** - Learn patterns from user corrections
2. **Custom pattern library** - Industry-specific patterns
3. **Multi-language support** - Japanese, Korean financial terms
4. **Fuzzy matching** - Handle typos in headers
5. **Context-aware classification** - Use surrounding data for hints

## References

- **Implementation**: `src/parsers/column_classifier.py`
- **Integration**: `src/parsers/account_hierarchy_parser.py`
- **MCP Entry Point**: `src/mcp_server/server.py`
- **Tests**: `test_column_intelligence.py`, `test_mcp_column_intelligence.py`

## Summary

Column Intelligence makes the financial parser **truly intelligent** by:
- Understanding column purpose from headers
- Making smart decisions about data usage
- Preventing common calculation errors automatically
- Providing transparency and validation

**Key Takeaway**: The system now reads Excel files like a human accountant would - understanding that "合计" is a subtotal (don't double count!), "备注" is just notes (exclude!), and "占比" is percentages (not absolute values!).