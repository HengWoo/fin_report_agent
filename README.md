# Financial Analysis Agent

A production-ready financial reporting agent that processes Excel files and generates bilingual business analysis for any type of business using **transparent tools + Claude's intelligence**.

**🆕 Now available in TWO deployment options:**
- **🎯 Agent Skill** (NEW!): Lightweight, zero-installation, works everywhere
- **🔧 MCP Server** (Existing): Full-featured with 15 tools, memory, validation workflows

## 🎯 Philosophy: Transparent Tools + Claude Intelligence

This system uses intelligent financial analysis that works transparently with Claude. No black-box automation - every step is visible and explainable.

### Why This Approach?

- ✅ **Transparent**: Every decision visible to user
- ✅ **Flexible**: Works with ANY Excel format
- ✅ **Accurate**: Prevents double-counting errors (e.g., saved ¥124,274 in our test)
- ✅ **Explainable**: Users can follow Claude's step-by-step reasoning
- ✅ **Maintainable**: Clean, modular architecture

## 🤔 Which Option Should I Use?

### Quick Decision Guide

```
┌─────────────────────────────────────────────────────────┐
│  Need quick analysis on any Claude platform?            │
│  → Use Agent Skill (zero installation!)                 │
├─────────────────────────────────────────────────────────┤
│  Need advanced features like memory, validation         │
│  workflows, and multi-turn intelligence?                │
│  → Use MCP Server (power user option)                   │
└─────────────────────────────────────────────────────────┘
```

### Detailed Comparison

| Feature | Agent Skill 🎯 | MCP Server 🔧 |
|---------|---------------|---------------|
| **Installation** | None (just add skill) | Requires `uv` + Python |
| **Platform Support** | All Claude platforms | Claude Code, Claude Desktop |
| **Mobile Support** | ✅ Yes (Claude.ai app) | ❌ No |
| **Setup Time** | < 1 minute | ~5 minutes |
| **Tool Access** | Uses Claude's native tools | 15 specialized MCP tools |
| **Memory System** | No persistent memory | ✅ Session memory + insights |
| **Validation Workflows** | Basic | ✅ Advanced (account hierarchy) |
| **Multi-turn Intelligence** | Yes | ✅ Enhanced (LSP-like navigation) |
| **Context Usage** | Low (progressive disclosure) | Higher (all tools loaded) |
| **Best For** | Quick analysis, beginners | Power users, complex workflows |

### Typical User Journey

```
Day 1:  Start with Agent Skill (zero friction) ──────┐
  ↓                                                    │
Day 7:  Realize you need validation workflows         │
  ↓                                                    │
Day 14: Install MCP Server for advanced features ←────┘
  ↓
Day 30: Use BOTH (Skill for quick checks, MCP for deep analysis)
```

## 🚀 Quick Start

### Option 1: Agent Skill (NEW! - Recommended for Most Users)

**Installation**: Just add the skill to your Claude environment

#### For Claude Code:
```bash
# Copy skill to your project
cp -r .claude/skills/financial-analysis ~/.claude/skills/
```

#### For Claude.ai:
1. Download the skill as ZIP: `.claude/skills/financial-analysis.zip`
2. Go to Claude.ai → Settings → Skills → Upload Skill
3. Upload the ZIP file

#### For Claude API:
```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    skill_id="financial-analysis",  # Your uploaded skill ID
    messages=[{
        "role": "user",
        "content": "Analyze my financial report @report.xlsx"
    }]
)
```

**That's it!** No Python, no dependencies, no MCP configuration needed.

**Next Steps**: Simply ask Claude to analyze your financial Excel files:
```
Claude, please analyze @restaurant_financial_report.xlsx
```

---

### Option 2: MCP Server (For Power Users)

#### For Claude Code (Recommended)

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

## 🛠️ Features Comparison

### Agent Skill Features 🎯

The Agent Skill provides comprehensive financial analysis capabilities using Claude's intelligence:

**✨ Core Capabilities:**
- **Excel Analysis**: Automatic structure recognition and data extraction
- **Bilingual Support**: Full Chinese/English parallel analysis
- **Industry Benchmarking**: Restaurant, retail, services, manufacturing, e-commerce, general business
- **KPI Calculation**: Revenue, costs, margins, efficiency metrics
- **Validation**: Double-counting prevention and assumption documentation
- **Trend Analysis**: Multi-period comparison and growth tracking
- **Strategic Insights**: Actionable recommendations based on data

**📚 Knowledge Resources:**
- 400+ Chinese-English financial term mappings
- 6 industry benchmark databases (restaurant, retail, services, etc.)
- Regional adjustments (China tier 1/2/3 cities)
- Business lifecycle considerations (startup, growth, mature)

**🎯 Best Use Cases:**
- Quick ad-hoc financial analysis
- Mobile analysis (Claude.ai app)
- Beginner-friendly financial insights
- Cross-platform consistency
- Low context overhead requirements

---

### MCP Server Features 🔧

The MCP Server provides **15 specialized tools** organized into 5 categories for power users:

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

### For Agent Skill Users:
- **`.claude/skills/financial-analysis/SKILL.md`**: Complete skill instructions and methodology
- **`.claude/skills/financial-analysis/EXAMPLES.md`**: Real-world usage examples and templates
- **`.claude/skills/financial-analysis/templates/`**: Financial terms and industry benchmarks

### For MCP Server Users:
- **CLAUDE.md**: Comprehensive project guide for Claude Code
- **Serena Memory**: `.serena/memory/simple_tools_breakthrough.md` - Documents the paradigm shift

### General:
- **README.md** (this file): Quick start and feature comparison

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