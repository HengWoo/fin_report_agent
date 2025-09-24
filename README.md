# Restaurant Financial Analysis Agent

A production-ready financial reporting agent that processes Chinese restaurant Excel files and generates bilingual business analysis using **simple tools + Claude's intelligence**.

## 🎯 Philosophy: Simple Tools + Claude Intelligence

This system uses **5 simple tools (~150 lines)** that return raw data to Claude, who then intelligently analyzes it. No complex parsers, no hardcoded logic - just transparent, explainable analysis.

### Why This Approach?

- ✅ **Transparent**: Every decision visible to user
- ✅ **Flexible**: Works with ANY Excel format
- ✅ **Accurate**: Prevents double-counting errors (e.g., saved ¥124,274 in our test)
- ✅ **Explainable**: Users can follow Claude's step-by-step reasoning
- ✅ **Maintainable**: 150 lines vs 3000+ lines of complex parsers

## 🚀 Quick Start (One Command!)

### Installation

**Using uv (recommended - fastest):**
```bash
uv tool install git+https://github.com/HengWoo/fin_report_agent
```

**Using pip:**
```bash
pip install git+https://github.com/HengWoo/fin_report_agent
```

### Setup with Claude Desktop

**Option 1: Auto-setup (recommended)**
```bash
restaurant-mcp setup-claude
# Follow the instructions to add configuration to Claude Desktop
```

**Option 2: Auto-setup with flag (fully automatic)**
```bash
restaurant-mcp setup-claude --auto
# Automatically writes config to Claude Desktop!
```

**Option 3: Manual setup**
Add to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "fin-report-agent": {
      "type": "stdio",
      "command": "restaurant-mcp",
      "args": ["start-server", "--transport", "stdio"]
    }
  }
}
```

### Use the Agent

Simply ask Claude in natural language:

```
Claude，请分析 @my_restaurant_report.xlsx
```

or

```
Analyze my restaurant's profitability @financial_report.xlsx
```

Claude will intelligently:
1. Explore the Excel structure
2. Identify key columns (subtotals, periods, etc.)
3. Extract relevant data
4. Generate comprehensive bilingual analysis

### Verify Installation

```bash
# Test that everything works
restaurant-mcp test
```

## 🛠️ The 5 Simple Tools

1. **get_excel_info**: Get file structure (rows, columns, sheets)
2. **show_excel_visual**: Display data in readable format
3. **search_in_excel**: Find cells containing specific terms
4. **read_excel_region**: Extract rectangular regions (raw data)
5. **calculate**: Basic math operations (sum, average, max, min)

## 📊 Real-World Success

**Test Case**: 野百灵餐厅（绵阳店）5-8月财务报表

**Challenge**: Original system reported ¥198,180.28 due to double-counting
**Solution**: Claude intelligently recognized subtotal columns
**Result**: Correct value ¥73,906.01 identified with transparent reasoning

**Full Analysis Delivered**:
- Revenue breakdown and trends
- Cost analysis (food, labor, expenses)
- KPI calculations and benchmarking
- Risk alerts and recommendations
- Bilingual output (Chinese/English)

## 📁 Project Structure

```
fin_report_agent/
├── run_mcp_server.py          # Entry point for MCP server
├── test_simple_tools_demo.py  # Demo of simple tools approach
├── src/
│   └── mcp_server/
│       ├── server.py          # MCP server implementation
│       ├── simple_tools.py    # 5 simple tools
│       └── config.py          # Server configuration
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
- KPI calculations (food cost %, labor cost %, prime cost)
- Trend analysis
- Risk alerts and recommendations

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