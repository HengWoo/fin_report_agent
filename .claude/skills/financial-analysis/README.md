# Financial Analysis Agent Skill

**Version**: 1.0
**Last Updated**: November 21, 2025
**Category**: Financial Analysis, Business Intelligence, Bilingual Analysis

## What is This?

This is a **Claude Agent Skill** that transforms Claude into an expert financial analyst specializing in bilingual (Chinese/English) business report analysis. When installed, Claude automatically recognizes financial analysis requests and provides comprehensive, benchmarked insights.

## Quick Start

### Installation

#### For Claude Code:
```bash
# Copy to your personal skills directory
cp -r . ~/.claude/skills/financial-analysis
```

#### For Claude.ai:
1. Create a ZIP file of this directory
2. Go to Claude.ai → Settings → Skills
3. Click "Upload Skill" and select the ZIP file

#### For Claude API:
Upload this skill directory to your Claude workspace and reference by skill_id

### Using the Skill

Simply ask Claude to analyze your financial reports:

```
Claude, please analyze @restaurant_financial_june.xlsx
```

Claude will automatically:
1. ✅ Detect it's a financial analysis request
2. ✅ Load the financial analysis skill
3. ✅ Read and understand your Excel structure
4. ✅ Validate account hierarchy (prevent double-counting)
5. ✅ Calculate KPIs and compare to industry benchmarks
6. ✅ Generate bilingual comprehensive analysis

## What's Included

### 📄 SKILL.md
The main skill instruction file containing:
- 8,000+ words of financial analysis expertise
- Bilingual financial terminology (Chinese/English)
- Industry benchmarking frameworks (6 industries)
- Validation workflows and best practices
- Report generation templates
- Quality assurance checklists

### 📚 EXAMPLES.md
Real-world usage examples including:
- Complete restaurant financial analysis walkthrough
- Quick question responses (e.g., "What's my food cost %?")
- Multi-period trend analysis
- Industry benchmarking reports
- Platform-specific notes (Claude Code, Claude.ai, API)

### 📊 templates/financial_terms_cn_en.json
Comprehensive Chinese-English financial terminology mapping:
- 400+ term mappings across 15 categories
- Revenue accounts (营业收入, 食品收入, etc.)
- Cost accounts (成本, 材料成本, etc.)
- Expense accounts (费用, 人工成本, 租金, etc.)
- Financial statements (损益表, 资产负债表, etc.)
- Time periods (月度, 季度, 年度, etc.)

### 📈 templates/industry_benchmarks.json
Industry financial benchmarks for 6+ business types:
- **Restaurant**: Prime cost, food cost %, labor cost %, profitability
- **Retail**: COGS%, margins, inventory turnover
- **Services**: Labor-intensive benchmarks, utilization rates
- **Manufacturing**: Material costs, production efficiency
- **E-commerce**: Fulfillment costs, conversion rates, CAC
- **General Business**: Conservative baseline benchmarks

Plus regional adjustments (China tier 1/2/3 cities) and business lifecycle considerations.

## Capabilities

### Core Analysis Features

✅ **Excel Structure Recognition**
- Automatic detection of income statements, P&L reports
- Multi-period column identification (monthly, quarterly, yearly)
- Account hierarchy parsing (parent-child relationships)
- Chinese/English mixed format support

✅ **Bilingual Financial Analysis**
- Parallel English/Chinese report generation
- Cultural context preservation
- Professional financial terminology
- Automatic language detection

✅ **Industry Benchmarking**
- 6 industry databases (restaurant, retail, services, manufacturing, e-commerce, general)
- Regional adjustments (China tier 1/2/3 cities)
- Business lifecycle considerations (startup, growth, mature)
- Performance scoring and grading

✅ **Advanced Validation**
- Parent-child account validation (prevent double-counting)
- Assumption documentation and verification
- Data quality assessment
- Calculation transparency

✅ **Strategic Insights**
- Revenue and cost breakdown analysis
- Margin calculations (gross, operating, net)
- Trend analysis (multi-period comparison)
- Actionable recommendations with expected impact

### Financial Expertise Areas

**Income Statement Analysis**
- Revenue composition and trends
- Cost structure optimization
- Expense ratio analysis
- Profitability assessment

**Key Performance Indicators**
- Prime cost ratio (for restaurants)
- Gross margin / Operating margin / Net margin
- Efficiency metrics (inventory turnover, utilization rates)
- Growth rates and variance analysis

**Industry Comparison**
- Benchmark against industry standards
- Competitive positioning assessment
- Performance scorecards
- Strength/weakness identification

**Multi-turn Intelligence**
- Progressive analysis refinement
- Context preservation across questions
- Follow-up question support
- Detailed drill-down capabilities

## Language Support

### Chinese Financial Terms
The skill has deep knowledge of Chinese financial terminology:

- **Revenue**: 营业收入, 主营业务收入, 食品收入, 酒水收入
- **Costs**: 营业成本, 食品成本, 材料成本, 生产成本
- **Expenses**: 营业费用, 人工成本, 租金, 水电费, 折旧
- **Profit**: 毛利润, 营业利润, 净利润
- **Statements**: 损益表, 资产负债表, 现金流量表

### Bilingual Output
All analyses can be delivered in:
- English only
- Chinese only (中文)
- Bilingual (parallel English/Chinese) ← Default for Chinese data

## Industry Support

### Supported Industries

1. **Restaurant / Food & Beverage** (餐饮业)
   - Prime cost ratio benchmarks (<60%)
   - Food cost % (28-35%)
   - Labor cost % (25-35%)
   - Table turnover optimization

2. **Retail** (零售业)
   - COGS benchmarks (50-75%)
   - Inventory turnover (5-15x/year)
   - Revenue per square foot

3. **Professional Services** (服务业)
   - High labor cost benchmarks (40-60%)
   - Utilization rate tracking
   - Revenue per employee

4. **Manufacturing** (制造业)
   - Raw material cost (40-60%)
   - Manufacturing overhead (15-25%)
   - Capacity utilization

5. **E-commerce** (电商)
   - Fulfillment costs (8-15%)
   - Digital marketing (10-25%)
   - Conversion rate optimization

6. **General Business** (通用)
   - Conservative baseline benchmarks
   - Applicable when specific industry unknown

## Example Use Cases

### ✅ Perfect For:

- **CFOs/Finance Teams**: Quick monthly/quarterly report analysis
- **Restaurant Owners**: Performance vs industry standards
- **Retail Managers**: Margin and inventory optimization
- **Business Analysts**: Competitive benchmarking
- **Investors**: Due diligence on financial statements
- **Consultants**: Client business health assessment
- **Entrepreneurs**: Understanding their own numbers

### ❌ Not Suitable For:

- Tax return preparation (requires CPA)
- Audit-level financial verification
- Investment advice (not financial advice)
- Legal/compliance matters
- Complex derivative valuations
- Forensic accounting

## Technical Details

### How It Works

**Progressive Disclosure Architecture:**
```
Level 1: Metadata (Always Loaded)
├── Skill name: "financial-analysis"
├── Description: Triggers on financial analysis requests
└── ~100 tokens

Level 2: Instructions (Loaded When Triggered)
├── Complete SKILL.md content
├── Financial analysis methodology
├── Bilingual terminology
└── ~5,000 tokens

Level 3: Resources (Loaded As Needed)
├── financial_terms_cn_en.json (referenced when needed)
├── industry_benchmarks.json (loaded for specific industries)
└── 0 tokens until accessed
```

This minimizes context window usage while providing full expertise when needed.

### Activation Triggers

The skill automatically activates when:
- User uploads/mentions Excel files with financial data
- Keywords detected: "financial analysis", "income statement", "P&L", "损益表"
- Questions about: revenue, costs, profitability, margins, KPIs
- Chinese financial terms mentioned: 营业收入, 成本, 费用, 利润

### Platform Compatibility

| Platform | Support | Notes |
|----------|---------|-------|
| Claude Code | ✅ Full | Best experience with file access |
| Claude.ai Web | ✅ Full | Upload Excel via attachment |
| Claude.ai Mobile | ✅ Full | Great for on-the-go analysis |
| Claude API | ✅ Full | Use skill_id parameter |
| Claude Agent SDK | ✅ Full | Load via .claude/skills/ |
| Claude Desktop | ✅ Full | Personal skills in ~/.claude/skills/ |

## Comparison to MCP Server

This skill complements (not replaces) the Financial Analysis MCP Server:

| Feature | Agent Skill | MCP Server |
|---------|-------------|------------|
| Installation | Zero (just add) | Requires Python + uv |
| Platform Support | All platforms | Claude Code/Desktop only |
| Tools Available | Uses Claude's native tools | 15 specialized MCP tools |
| Memory System | No persistence | Session memory + insights |
| Validation Workflows | Basic | Advanced (hierarchy parser) |
| Context Overhead | Low (progressive) | Higher (all tools loaded) |
| Best For | Quick analysis | Complex workflows |

**Recommended**: Start with the skill, upgrade to MCP server if you need advanced features.

## File Structure

```
financial-analysis/
├── README.md                          # This file
├── SKILL.md                           # Main skill instructions (8,000+ words)
├── EXAMPLES.md                        # Usage examples and templates
└── templates/
    ├── financial_terms_cn_en.json     # 400+ Chinese-English term mappings
    └── industry_benchmarks.json       # 6 industry benchmark databases
```

## Version History

### v1.0 (2025-11-21)
- Initial release
- 8,000+ word comprehensive financial analysis expertise
- 400+ Chinese-English financial term mappings
- 6 industry benchmark databases
- Bilingual report generation templates
- Validation workflows for accuracy
- Regional adjustments (China tier 1/2/3 cities)

## Support & Feedback

- **Documentation**: See `SKILL.md` for detailed methodology
- **Examples**: See `EXAMPLES.md` for real-world usage
- **Issues**: Report at https://github.com/HengWoo/fin_report_agent/issues
- **Discussions**: GitHub Discussions for questions and ideas

## License

[Your License Here]

---

**Built with expertise in:**
- Financial analysis
- Chinese/English bilingual business terminology
- Industry benchmarking frameworks
- Claude Agent Skills architecture
- Progressive disclosure patterns

**Inspired by:**
- Professional financial analysis best practices
- Multi-turn intelligence (Serena project)
- Real-world financial reporting needs
- Cross-cultural business communication

---

**Ready to get started?** Just ask Claude: "Analyze my financial report @file.xlsx"
