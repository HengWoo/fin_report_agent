# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A production-ready financial reporting agent that processes Chinese restaurant Excel files and generates bilingual business analysis. Built using Claude Code SDK with MCP (Model Context Protocol) server integration for AI-powered analysis.

**Package Name:** `fin-report-agent`
**MCP Server Name:** `fin-report-agent`
**GitHub:** https://github.com/HengWoo/fin_report_agent

### Recent Major Updates (2025-09-24)

**✅ Complete Renaming & Branding:**
- Unified all names to `fin-report-agent` (was `restaurant-mcp`, `restaurant-financial-analysis`)
- Updated CLI commands, MCP server name, package name, and all documentation
- Consistent naming across Claude Code and Claude Desktop

**✅ Claude Code Support Added:**
- One-command installation: `claude mcp add fin-report-agent -- uvx ...`
- Per-project configuration
- No global installation needed

**✅ Claude Desktop Auto-Configuration:**
- `fin-report-agent setup-claude --auto` automatically writes config
- Detects config locations across platforms (macOS, Linux)
- Fallback to manual instructions if needed

## Essential Commands

### Environment and Dependencies
```bash
# Install dependencies
uv sync

# Run MCP server for Claude Code integration
uv run python run_mcp_server.py
```

### Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_chinese_excel_parser.py -v
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/
```

### MCP Server Management
```bash
# Test the MCP server locally
uv run fin-report-agent test

# Run MCP server for development
uv run fin-report-agent start-server --transport stdio

# Check MCP server status in Claude Code
claude mcp list

# Get server details
claude mcp get fin-report-agent
```

## Architecture Overview

### Core Data Flow

**🎯 NEW: Simple Tools + Claude Intelligence (Recommended)**
```
Chinese Excel → Simple Tools (read/search/calculate) → Claude's Intelligence → Transparent Analysis → User
```

**🔧 LEGACY: Complex Parser Pipeline (For Compatibility)**
```
Chinese Excel → ChineseExcelParser → Pydantic Models → Restaurant Analytics → Bilingual Reporter → Claude Code
```

### Key Components

**MCP Server (`src/mcp_server/server.py`)**
- `RestaurantFinancialMCPServer`: Main server providing 6 financial analysis tools
- Tools: parse_excel, validate_financial_data, calculate_kpis, analyze_trends, generate_insights, comprehensive_analysis
- Integrates with Claude Code via Model Context Protocol

**Chinese Excel Parser (`src/parsers/chinese_excel_parser.py`)**
- Parses Chinese restaurant income statements with multi-period data
- Maps Chinese financial terms (营业收入, 食品成本, etc.) to standardized English equivalents
- Handles complex Excel layouts and header detection

**Restaurant Analytics (`src/analyzers/restaurant_analytics.py`)**
- Calculates restaurant-specific KPIs (food cost %, labor cost %, prime cost)
- Industry benchmarking (food cost 28-35%, labor 25-35%, prime cost <60%)
- Multi-period trend analysis and insights generation

**Financial Data Models (`src/models/financial_data.py`)**
- Pydantic V2 models for type-safe financial data handling
- `IncomeStatement`: Main structure with revenue, costs, expenses, metrics
- Comprehensive validation rules for restaurant financial data

### Bilingual Support Architecture

The system provides built-in English/Chinese bilingual analysis:

**Term Mapping System**
- Comprehensive Chinese-English financial term dictionary
- Cultural context preservation in translations
- Support for both simplified and traditional Chinese

**Bilingual Reporter (`src/mcp_server/bilingual_reporter.py`)**
- Generates parallel analysis in English and Chinese
- Maintains cultural business context
- Formats reports for different audiences (professional, investor, general)

## Installation & Distribution

### For End Users

**Claude Code (Recommended - One Command):**
```bash
claude mcp add fin-report-agent -- uvx --from git+https://github.com/HengWoo/fin_report_agent fin-report-agent start-server --transport stdio
```

**Claude Desktop (Auto-Configuration):**
```bash
# Step 1: Install globally
uv tool install git+https://github.com/HengWoo/fin_report_agent

# Step 2: Auto-configure
fin-report-agent setup-claude --auto

# Step 3: Restart Claude Desktop
```

**Key Differences:**
- **Claude Code**: Per-project, no installation, uses `uvx` on-the-fly, config in `.claude/mcp.json`
- **Claude Desktop**: Global install, auto-config writes to `~/.claude/mcp.json`

### CLI Commands Available

```bash
fin-report-agent test              # Test MCP server components
fin-report-agent setup-claude      # Show setup instructions
fin-report-agent setup-claude --auto  # Auto-configure Claude Desktop
fin-report-agent start-server      # Start MCP server (stdio/http)
```

## Integration with Claude Code

### MCP Server Tools Available to Claude

**🎯 Simple Tools (Recommended) - Claude-Driven Intelligence:**
1. **get_excel_info**: Get basic Excel file structure (rows, columns, sheets)
2. **show_excel_visual**: Display Excel data in readable format for Claude to analyze
3. **search_in_excel**: Find cells containing specific terms
4. **read_excel_region**: Extract rectangular regions of cells (raw data, no interpretation)
5. **calculate**: Simple math operations (sum, average, max, min)

**🔧 Complex Tools (Legacy) - For Compatibility:**
1. **comprehensive_analysis**: Complete Excel → insights pipeline
2. **parse_excel**: Parse Chinese restaurant Excel files
3. **calculate_kpis**: Calculate restaurant financial metrics
4. **analyze_trends**: Multi-period performance analysis
5. **validate_financial_data**: Validate against industry standards
6. **generate_insights**: Strategic business recommendations

### Usage Patterns

**✨ NEW: Claude as Intelligent Agent (Recommended Approach)**

The system now uses **simple tools + Claude's intelligence** instead of complex parsers:

**Example - Natural Language Analysis:**
```
User: "Claude，请分析 @野百灵餐厅财务报表.xlsx"

Claude's Workflow:
1. get_excel_info() → Understands file structure (139 rows, 28 columns)
2. show_excel_visual() → Examines layout, identifies column headers
3. search_in_excel("合计") → Discovers subtotal column at Col 25
4. search_in_excel("营业收入") → Finds revenue accounts
5. read_excel_region() → Extracts specific data intelligently
6. calculate() → Verifies calculations transparently
7. Generates comprehensive analysis with full reasoning visible
```

**Key Advantages:**
- ✅ **Transparent Reasoning**: Every decision visible to user
- ✅ **Flexible**: Works with ANY Excel format (not hardcoded)
- ✅ **Accurate**: Avoids double-counting errors (e.g., prevented ¥124,274 error)
- ✅ **Explainable**: User can follow Claude's step-by-step analysis
- ✅ **Simple**: ~150 lines of tool code vs 3000+ lines of complex parsers

**Real-World Success:**
- Successfully analyzed 野百灵餐厅 (Mianyang branch) 5-8月财务报表
- Correctly identified ¥73,906.01 (not ¥198,180.28) by intelligently recognizing subtotal columns
- Generated comprehensive bilingual analysis covering revenue, costs, expenses, and strategic insights

**Traditional Queries Still Supported:**
- "Analyze my restaurant's profitability compared to industry standards"
- "What are my biggest cost problems and how can I save money?"
- "请分析我的餐厅财务数据" (Chinese analysis requests)

**File Processing:**
- Place Excel files in project directory
- Reference by filename in Claude queries (@filename)
- Claude intelligently handles Chinese financial terminology
- No pre-configuration needed - Claude explores and understands structure

## 📋 Financial Analysis Validation Workflow

### MANDATORY VALIDATION PROTOCOL

**🚨 CRITICAL: NEVER perform financial calculations without completing validation workflow!**

#### Step-by-Step Validation Process

**1. FIRST STEP: Account Structure Validation**
```bash
# Always start with structure validation
validate_account_structure tool → Shows hierarchy → Get user confirmation
```

**2. REQUIRED USER CONFIRMATIONS:**
- ✅ "Is this account structure correct?"
- ✅ "What depreciation/amortization periods apply?" (typically 3-5 years)
- ✅ "Should I use only leaf accounts to avoid double counting?"
- ✅ "What benchmarks/comparisons do you prefer?"

**3. ASSUMPTION DOCUMENTATION:**
- Document ALL user-confirmed assumptions
- Include validation steps performed in reports
- Show audit trail of decisions made

**4. CALCULATION PHASE:**
- Only proceed after user validates structure
- Use confirmed accounts and assumptions
- Show sensitivity to assumption changes

#### Example Validation Workflow

```
User: "Analyze my restaurant financial report"

Agent: Let me first validate the account structure:
[Calls validate_account_structure tool]

Agent: I found this hierarchy:
九、长期待摊费用 (¥24,635/month) [PARENT]
├── 设施设备 (¥4,613) [LEAF]
├── 新店装修 (¥24,684) [LEAF]
└── 新店开办 (¥26,543) [LEAF]

❓ VALIDATION QUESTIONS:
1. Is this account structure correct?
2. What depreciation period applies? (You mentioned 3 years)
3. Should I use only leaf accounts to avoid double counting?

User: "Yes, 3-year depreciation, use only leaf accounts"

Agent: ✅ Validated! Now calculating with confirmed assumptions...
Investment: ¥24,635 × 36 months = ¥886,860
[Proceeds with accurate analysis including assumption documentation]
```

#### Available MCP Tools for Validation

**Core Validation Tools:**
1. **`validate_account_structure`**: MANDATORY first step - shows hierarchy and asks for confirmation
2. **`parse_excel`**: Enhanced with validation requirements
3. **`comprehensive_analysis`**: Now requires validation workflow completion
4. **`adaptive_financial_analysis`**: Intelligent validation with user interaction

#### Validation Anti-Patterns (AVOID)

❌ **NEVER DO:**
- Calculate without showing account structure to user
- Assume depreciation periods without asking
- Use parent accounts when children exist (double counting)
- Skip assumption documentation
- Proceed with calculations after parsing errors

✅ **ALWAYS DO:**
- Show account hierarchy before calculations
- Get explicit user confirmation on assumptions
- Document all validation steps in reports
- Use only validated accounts for calculations
- Include sensitivity analysis for key assumptions

#### Integration with Serena Patterns

This validation framework follows Serena's approach:
- **Tool description overrides** inject validation requirements
- **Prompt engineering** enforces validation workflow
- **Context configurations** adapt to different analysis needs
- **Separation of concerns** keeps tools simple, intelligence in prompts

## Development Patterns

### Error Handling Strategy
- Multi-layer validation: data type → business rules → cross-reference → outlier detection
- Graceful degradation for partial data
- Circuit breaker patterns for error recovery
- Detailed error context for financial data issues

### Financial Data Validation
Restaurant-specific validation rules in `src/validators/restaurant_validator.py`:
- Prime cost ratio validation (target: <60%)
- Food cost percentage (industry: 28-35%)
- Labor cost percentage (industry: 25-35%)
- Revenue component reconciliation
- Seasonal pattern detection

### Testing Strategy
- Unit tests for each component (`tests/`)
- Integration tests for complete workflows (`test_end_to_end.py`)
- Real data testing with sample Excel files
- MCP server integration testing

## Chinese Financial Data Handling

### Supported Chinese Terms
| Chinese | English | Usage |
|---------|---------|-------|
| 营业收入 | Operating Revenue | Primary revenue category |
| 食品收入 | Food Revenue | Food sales tracking |
| 酒水收入 | Beverage Revenue | Drink sales tracking |
| 人工成本 | Labor Cost | Staff-related expenses |
| 食品成本 | Food Cost | COGS for food items |

### Excel File Requirements
- Sheet name: "损益表" (Income Statement)
- Multi-period columns with Chinese date headers
- Chinese financial terms in first column
- Numeric data in subsequent columns

## Performance Considerations

- Stream processing for large Excel files
- Caching for repeated calculations
- Parallel processing for multi-period analysis
- Memory-efficient data structures for financial calculations

## Security Notes

- Local processing only - no external data transmission
- Secure file access patterns for financial data
- Input sanitization for Excel files
- Audit trail for all financial operations