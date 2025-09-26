# Financial Analysis Agent

A production-ready financial reporting agent that processes Excel files and generates bilingual business analysis for any type of business using **transparent tools + Claude's intelligence**.

## 🎯 Philosophy: Transparent Tools + Claude Intelligence

This system uses **15 specialized tools** organized into 5 categories that work transparently with Claude for intelligent financial analysis. No black-box automation - every step is visible and explainable.

### Why This Approach?

- ✅ **Transparent**: Every decision visible to user
- ✅ **Flexible**: Works with ANY Excel format
- ✅ **Accurate**: Prevents double-counting errors (e.g., saved ¥124,274 in our test)
- ✅ **Explainable**: Users can follow Claude's step-by-step reasoning
- ✅ **Maintainable**: Clean, modular architecture with organized tool categories

## 🚀 Quick Start (One Command!)

### For Claude Code (Recommended)

From your project directory:

```bash
claude mcp add fin-report-agent -- uvx --from git+https://github.com/HengWoo/fin_report_agent fin-report-agent start-server --transport stdio
```

That's it! Claude Code automatically configures everything.

---

### For Claude Desktop

**Step 1: Install**
```bash
uv tool install git+https://github.com/HengWoo/fin_report_agent
```

**Step 2: Auto-configure**
```bash
fin-report-agent setup-claude --auto
```

**Step 3: Restart Claude Desktop**

---

### Manual Setup (if auto-config fails)

Add to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "fin-report-agent": {
      "type": "stdio",
      "command": "fin-report-agent",
      "args": ["start-server", "--transport", "stdio"]
    }
  }
}
```

### Use the Agent

Simply ask Claude in natural language:

```
Claude，请分析 @financial_report.xlsx
```

or

```
Analyze my business profitability @financial_report.xlsx
```

Claude will intelligently:
1. Explore the Excel structure
2. Identify key columns (subtotals, periods, etc.)
3. Extract relevant data
4. Generate comprehensive bilingual analysis

### Verify Installation

```bash
# Test that everything works
fin-report-agent test
```

## 🛠️ The 15 Specialized Tools

### 🎯 Simple Tools (5) - Data Extraction & Calculation
1. **get_excel_info**: Get file structure (rows, columns, sheets)
2. **show_excel_visual**: Display data in readable format
3. **search_in_excel**: Find cells containing specific terms
4. **read_excel_region**: Extract rectangular regions (raw data)
5. **calculate**: Basic math operations (sum, average, max, min)

### 🧭 Navigation Tools (3) - LSP-like Financial Navigation
6. **find_account**: Search financial accounts by name pattern
7. **get_financial_overview**: High-level financial structure overview
8. **get_account_context**: Get account with parent/children context

### 🤔 Thinking Tools (3) - Reflection & Validation
9. **think_about_financial_data**: Assess data sufficiency for analysis
10. **think_about_analysis_completeness**: Check analysis completeness
11. **think_about_assumptions**: Validate assumptions against best practices

### 💾 Memory Tools (3) - Session Management
12. **save_analysis_insight**: Store insights for future reference
13. **get_session_context**: View session history and progress
14. **write_memory_note**: Document patterns and knowledge

### 🔧 Validation Tools (1) - Structure Validation
15. **validate_account_structure**: MANDATORY validation before calculations

## 📊 Real-World Success

**Test Case**: 野百灵餐厅（绵阳店）5-8月财务报表 (Restaurant Financial Report)

**Challenge**: Complex Excel with mixed Chinese/English, potential double-counting risks
**Solution**:
- Step 1: `validate_account_structure` → User confirmed 3-year depreciation
- Step 2: Transparent data extraction using simple tools
- Step 3: Progressive analysis with thinking tools
- Step 4: Bilingual comprehensive report

**Results Achieved**:
- Total Revenue: ¥1,459,161 (accurate calculation)
- Net Profit Margin: 18.3% (excellent vs industry 5-10%)
- Cost Structure Analysis: Food 35.4%, Labor 24.5%, Rent 6.6%
- Strategic Recommendations: Launch delivery service, optimize costs
- Full audit trail of all assumptions and calculations

## 📁 Project Structure

```
fin_report_agent/
├── run_mcp_server.py          # Entry point for MCP server
├── test_simple_tools_demo.py  # Demo of simple tools approach
├── src/
│   └── mcp_server/
│       ├── server.py          # Main MCP server (FinancialAnalysisMCPServer)
│       ├── handler_router.py  # Routes tools to appropriate handlers
│       ├── tool_registry.py   # All 15 tool definitions
│       └── handlers/          # Organized tool handlers
│           ├── simple_tools_handler.py     # 5 simple tools
│           ├── navigation_handler.py       # 3 navigation tools
│           ├── thinking_handler.py         # 3 thinking tools
│           ├── memory_handler.py           # 3 memory tools
│           └── complex_analysis_handler.py # 1 validation tool
├── tests/                     # Unit and integration tests
├── .mcp.json                  # MCP configuration for Claude Code
├── CLAUDE.md                  # Detailed project documentation
├── pyproject.toml             # Python dependencies
└── archive/                   # Old implementation (for reference)
```

## 🔧 Development

### Running the MCP Server

```bash
uv run python run_mcp_server.py
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run simple tools demo
uv run python test_simple_tools_demo.py
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/
```

## 📚 Documentation

- **CLAUDE.md**: Comprehensive project guide for Claude Code
- **Serena Memory**: `.serena/memory/simple_tools_breakthrough.md` - Documents the paradigm shift

## 🎯 Key Features

### Intelligent Analysis
- Automatic column type detection (periods, subtotals, ratios, notes)
- Parent-child account validation
- Cross-verification of calculations
- Industry benchmarking

### Bilingual Support
- English/Chinese parallel analysis
- Cultural context preservation
- Professional financial terminology

### Financial Insights
- Revenue and cost breakdown
- KPI calculations (customizable by industry)
- Multi-period trend analysis
- Risk alerts and strategic recommendations
- Industry benchmarking and performance scoring

## 🔐 Security

- Local processing only (no external data transmission)
- Secure file access patterns
- Input sanitization for Excel files
- Audit trail for all operations

## 📝 License

[Your License Here]

## 🤝 Contributing

[Your contribution guidelines]

## 📞 Support

[Your support information]

---

**Built with Claude Code** - [claude.ai/code](https://claude.ai/code)