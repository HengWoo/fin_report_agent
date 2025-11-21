# Financial Analysis Skill - Usage Examples

This document provides practical examples of how the Financial Analysis Skill works in real-world scenarios.

## Quick Reference

**Skill Name**: `financial-analysis`
**Activation**: Automatic when user mentions financial reports, Excel files, or analysis requests
**Platforms**: Claude Code, Claude.ai, Claude API, Claude Agent SDK
**Languages**: English, Chinese (中文), Bilingual

---

## Example 1: Complete Restaurant Financial Analysis

### User Request
```
Claude, please analyze @restaurant_financial_june.xlsx
```

### Claude's Response Flow

**Step 1: Initial Assessment**
```
I'll analyze your restaurant financial report. Let me examine the structure...

[Reads Excel file]

I can see this is a Chinese income statement (损益表) with:
- 139 rows of financial data
- 5 period columns: May (5月), June (6月), July (7月), August (8月), Total (合计)
- Account hierarchy with Chinese financial terms (营业收入, 成本, 费用)

Let me identify the account structure to ensure accurate calculations...
```

**Step 2: Structure Validation**
```markdown
## Account Structure Identified

**Revenue (营业收入):**
├── Food Revenue (食品收入)
└── Beverage Revenue (酒水收入)

**Costs (成本):**
├── Food Cost (食品成本)
└── Beverage Cost (酒水成本)

**Operating Expenses (营业费用):**
├── Labor Cost (人工成本)
├── Rent (租金)
├── Utilities (水电费)
├── Depreciation (折旧)
└── Other expenses

**Long-term Prepaid Expenses (长期待摊费用):**
├── Equipment (设施设备): ¥4,613/month
├── Renovation (新店装修): ¥24,684/month
└── Opening Costs (新店开办): ¥26,543/month
**Total**: ¥24,635/month

❓ **Validation Questions:**
1. I see long-term prepaid expenses of ¥24,635/month. What amortization period
   should I use for calculating the total investment?
   (Common: 3 years = 36 months, 5 years = 60 months)

2. Should I compare your performance against restaurant industry benchmarks?

3. Would you like the analysis in English, Chinese, or both languages?
```

**Step 3: User Confirmation**
```
User: "Use 3 years (36 months) for amortization. Yes to benchmarking. Both languages please."
```

**Step 4: Comprehensive Analysis**
```markdown
# Financial Analysis Report | 财务分析报告

**Business**: 野百灵餐厅（绵阳店） | Yebailing Restaurant (Mianyang Branch)
**Period**: May - August 2024 | 2024年5-8月
**Analysis Date**: November 21, 2025 | 2025年11月21日

---

## Executive Summary | 执行摘要

### Key Performance Indicators | 关键绩效指标

| Metric | 指标 | Value | 数值 | Industry Benchmark | 行业基准 | Assessment | 评估 |
|--------|------|-------|------|-------------------|----------|------------|------|
| Total Revenue | 总收入 | ¥1,459,161 | ¥1,459,161 | - | - | - | - |
| Net Profit | 净利润 | ¥267,234 | ¥267,234 | - | - | - | - |
| Net Profit Margin | 净利润率 | 18.3% | 18.3% | 5-10% | 5-10% | ⭐ Excellent | ⭐ 优秀 |
| Prime Cost Ratio | 综合成本率 | 59.9% | 59.9% | <60% | <60% | ✅ Good | ✅ 良好 |
| Food Cost % | 食品成本率 | 35.4% | 35.4% | 28-35% | 28-35% | ⚠️ Upper Limit | ⚠️ 上限 |
| Labor Cost % | 人工成本率 | 24.5% | 24.5% | 25-35% | 25-35% | ✅ Excellent | ✅ 优秀 |

### Overall Performance | 总体表现
**Rating**: ⭐⭐⭐⭐☆ (4/5 Stars - Excellent)
**评级**: ⭐⭐⭐⭐☆ (4/5星 - 优秀)

Your restaurant is performing significantly above industry standards with an 18.3% net profit
margin, nearly double the typical 5-10% range for restaurants.

您的餐厅表现显著优于行业标准，净利润率达到18.3%，几乎是餐饮行业典型5-10%区间的两倍。

---

## Revenue Analysis | 收入分析

### Total Revenue | 总收入: ¥1,459,161

**Monthly Breakdown | 月度明细:**
- May (5月): ¥346,725
- June (6月): ¥362,890
- July (7月): ¥374,112
- August (8月): ¥375,434

**Growth Trend | 增长趋势**: +8.3% (May to August)

### Revenue Composition | 收入构成

| Category | 类别 | Amount | 金额 | % of Total | 占比 |
|----------|------|---------|------|------------|------|
| Food Revenue | 食品收入 | ¥1,094,371 | ¥1,094,371 | 75.0% | 75.0% |
| Beverage Revenue | 酒水收入 | ¥364,790 | ¥364,790 | 25.0% | 25.0% |

**Insights | 洞察:**
- Revenue is growing steadily (+8.3% from May to August), indicating strong market acceptance
- Food-to-beverage ratio (75:25) is within healthy range for full-service restaurants
- Average monthly revenue: ¥364,790

- 收入稳步增长（5月至8月增长8.3%），表明市场接受度良好
- 食品与酒水比例（75:25）在全服务餐厅的健康范围内
- 月均收入：¥364,790

---

## Cost Structure Analysis | 成本结构分析

### Prime Costs | 综合成本

| Cost Type | 成本类型 | Amount | 金额 | % of Revenue | 占收入比 | Benchmark | 基准 |
|-----------|---------|---------|------|--------------|----------|-----------|------|
| Food & Beverage Cost | 食品酒水成本 | ¥516,959 | ¥516,959 | 35.4% | 35.4% | 28-35% | 28-35% |
| Labor Cost | 人工成本 | ¥357,495 | ¥357,495 | 24.5% | 24.5% | 25-35% | 25-35% |
| **Prime Cost Total** | **综合成本合计** | **¥874,454** | **¥874,454** | **59.9%** | **59.9%** | **<60%** | **<60%** |

**Assessment | 评估**: ✅ **Just within target** - Prime cost ratio of 59.9% is barely within the
critical <60% threshold for healthy restaurant operations.

**评估**: ✅ **刚好达标** - 综合成本率59.9%刚好在健康餐饮运营的关键阈值<60%以内。

### Operating Expenses Breakdown | 营业费用明细

| Expense Type | 费用类型 | Amount | 金额 | % of Revenue | 占收入比 | Benchmark | 基准 |
|--------------|---------|---------|------|--------------|----------|-----------|------|
| Rent | 租金 | ¥96,000 | ¥96,000 | 6.6% | 6.6% | 5-10% | 5-10% |
| Utilities | 水电燃气费 | ¥58,245 | ¥58,245 | 4.0% | 4.0% | 3-5% | 3-5% |
| Depreciation | 折旧摊销 | ¥98,540 | ¥98,540 | 6.8% | 6.8% | - | - |
| Other Operating Expenses | 其他营业费用 | ¥63,888 | ¥63,888 | 4.4% | 4.4% | - | - |
| **Total Operating Expenses** | **营业费用合计** | **¥316,673** | **¥316,673** | **21.7%** | **21.7%** | **15-25%** | **15-25%** |

---

## Profitability Analysis | 盈利能力分析

### Margin Analysis | 利润率分析

| Margin Type | 利润率类型 | Amount | 金额 | Percentage | 百分比 | Benchmark | 基准 | Score | 评分 |
|-------------|-----------|---------|------|------------|--------|-----------|------|-------|------|
| Gross Profit | 毛利润 | ¥942,202 | ¥942,202 | 64.6% | 64.6% | 60-70% | 60-70% | ★★★★☆ | ★★★★☆ |
| Operating Profit | 营业利润 | ¥584,707 | ¥584,707 | 40.1% | 40.1% | 10-20% | 10-20% | ★★★★★ | ★★★★★ |
| Net Profit | 净利润 | ¥267,234 | ¥267,234 | 18.3% | 18.3% | 5-10% | 5-10% | ★★★★★ | ★★★★★ |

### Industry Comparison | 行业对比

```
Your Performance vs Industry Average:
您的表现 vs 行业平均:

Net Profit Margin:
净利润率:
Industry Average: ████░░░░░░ 7.5%
行业平均:       ████░░░░░░ 7.5%

Your Business:    ████████████████████ 18.3% ⭐ +10.8 points!
您的业务:         ████████████████████ 18.3% ⭐ +10.8个百分点！
```

**Analysis | 分析:**
- Your net profit margin (18.3%) is **2.4× higher** than industry average (7.5%)
- This exceptional performance indicates excellent operational efficiency
- Strong pricing power and cost control

- 您的净利润率（18.3%）比行业平均水平（7.5%）**高出2.4倍**
- 这一卓越表现表明运营效率极佳
- 定价能力和成本控制能力强

---

## Long-term Investment Analysis | 长期投资分析

### Prepaid Expenses Calculation | 待摊费用计算

**Assumption Confirmed | 已确认假设**: 3-year amortization period (36 months)
**已确认假设**: 3年摊销期（36个月）

| Item | 项目 | Monthly Amount | 月度金额 | Total Investment | 总投资 |
|------|------|----------------|----------|-----------------|--------|
| Equipment | 设施设备 | ¥4,613 | ¥4,613 | ¥166,068 | ¥166,068 |
| Renovation | 新店装修 | ¥24,684 | ¥24,684 | ¥888,624 | ¥888,624 |
| Opening Costs | 新店开办 | ¥26,543 | ¥26,543 | ¥955,548 | ¥955,548 |
| **Total** | **合计** | **¥55,840** | **¥55,840** | **¥2,010,240** | **¥2,010,240** |

**Note**: Monthly depreciation charged in P&L is ¥24,635 (less than sum above due to different
useful lives for different asset categories).

**说明**: 损益表中的月度折旧为¥24,635（低于上述总和是因为不同资产类别的使用年限不同）。

### Return on Investment (ROI) | 投资回报率

**4-Month Performance | 4个月表现:**
- Total Investment | 总投资: ¥2,010,240
- 4-Month Net Profit | 4个月净利润: ¥267,234
- Annualized Net Profit | 年化净利润: ¥800,702 (¥267,234 × 3)
- **Simple Payback Period | 简单回收期**: 2.5 years

**Assessment | 评估**: ✅ **Excellent** - With 18.3% net margin and 2.5-year payback period,
this restaurant represents a strong investment.

**评估**: ✅ **优秀** - 以18.3%的净利润率和2.5年的回收期来看，这家餐厅是一项稳健的投资。

---

## Strategic Recommendations | 战略建议

### 🎯 Priority 1: Food Cost Optimization | 优先级1：食品成本优化

**Current Status | 当前状况**: Food cost at 35.4% (upper limit of 28-35% benchmark)
**当前状况**: 食品成本率35.4%（处于28-35%基准的上限）

**Recommendations | 建议:**
1. **Portion Control | 份量控制**: Implement standardized recipes and portion sizes
   - Expected Impact: Reduce food cost by 2-3 percentage points
   - 预期影响：降低食品成本2-3个百分点

2. **Supplier Negotiation | 供应商谈判**: Leverage growing volume for better pricing
   - With ¥1.1M in food purchases over 4 months, you have negotiating power
   - 4个月食品采购额达¥110万，您拥有议价能力

3. **Menu Engineering | 菜单工程**: Focus on high-margin items
   - Analyze which dishes have best contribution margin
   - 分析哪些菜品的边际贡献最高

**Expected Financial Impact | 预期财务影响:**
```
If food cost reduced from 35.4% to 33%:
如果食品成本率从35.4%降至33%:

Additional Gross Profit: ¥35,020 (2.4% × ¥1,459,161)
额外毛利润: ¥35,020

New Net Profit Margin: 20.7% (from 18.3%)
新净利润率: 20.7%（从18.3%）
```

### 🎯 Priority 2: Revenue Growth Initiatives | 优先级2：收入增长举措

**Current Trend | 当前趋势**: +8.3% growth over 4 months (healthy)
**当前趋势**: 4个月增长8.3%（健康）

**Recommendations | 建议:**
1. **Delivery Services | 外卖服务**: Expand to food delivery platforms
   - Potential to add 20-30% incremental revenue
   - 有潜力增加20-30%的增量收入
   - Note: Consider delivery platform fees (10-20%) in profitability analysis
   - 注意：在盈利分析中考虑外卖平台费用（10-20%）

2. **Peak Hour Optimization | 高峰时段优化**: Improve table turnover during busy periods
   - Current: Estimate 2-3 turns/day
   - Target: 3-4 turns/day
   - Impact: 15-20% revenue increase with minimal cost increase
   - 影响：收入增长15-20%，成本增加极少

3. **Marketing Programs | 营销计划**: Loyalty programs and social media
   - Budget: 2-3% of revenue (currently have room in expense budget)
   - 预算：收入的2-3%（目前费用预算有空间）

### 🎯 Priority 3: Maintain Current Strengths | 优先级3：保持当前优势

**Strengths to Preserve | 需保持的优势:**
1. **Labor Efficiency | 人工效率**: 24.5% labor cost is excellent for full-service restaurant
   - Document current staffing model
   - 记录当前人员配置模型

2. **Cost Control Discipline | 成本控制纪律**: Operating expenses well-managed at 21.7%
   - Continue current procurement and expense approval processes
   - 继续当前的采购和费用审批流程

3. **Pricing Power | 定价能力**: High net margins indicate strong pricing
   - Maintain quality standards that justify premium pricing
   - 保持能支撑优质定价的质量标准

---

## Risk Areas to Monitor | 需监控的风险领域

### ⚠️ Risk 1: Food Cost Creep | 风险1：食品成本上升

**Alert | 警示**: Food cost at upper limit of benchmark (35.4%)
**警示**: 食品成本处于基准上限（35.4%）

**Monitoring Plan | 监控计划:**
- Track food cost % weekly
- Investigate immediately if exceeds 36%
- Review supplier prices and waste levels monthly
- 每周跟踪食品成本率
- 如超过36%立即调查
- 每月审核供应商价格和浪费水平

### ⚠️ Risk 2: Revenue Sustainability | 风险2：收入可持续性

**Question | 问题**: Can 8.3% quarterly growth be sustained?
**问题**: 8.3%的季度增长能否持续？

**Factors to Watch | 需关注的因素:**
- Seasonality effects (summer vs winter traffic)
- Local competition changes
- Economic conditions in Mianyang
- 季节性影响（夏季 vs 冬季客流）
- 当地竞争变化
- 绵阳经济状况

---

## Appendix | 附录

### Analysis Methodology | 分析方法

**Data Source | 数据来源**: restaurant_financial_june.xlsx
**Analysis Date | 分析日期**: November 21, 2025
**Period Covered | 涵盖期间**: May - August 2024 (4 months)

**Validation Steps Performed | 执行的验证步骤:**
1. ✅ Account hierarchy validated (parent-child relationships identified)
2. ✅ Only leaf accounts used for calculations (no double-counting)
3. ✅ User-confirmed assumptions documented (3-year amortization)
4. ✅ Industry benchmarks applied (restaurant industry standards)
5. ✅ Cross-verification of key totals against Excel file

### Key Assumptions | 关键假设

1. **Amortization Period | 摊销期**: 3 years (36 months) for long-term prepaid expenses
   - Source: User confirmation
   - 来源：用户确认

2. **Industry Benchmarks | 行业基准**: Restaurant industry standards (China)
   - Source: Industry research and historical data
   - 来源：行业研究和历史数据

3. **Annualization Method | 年化方法**: Simple multiplication (4-month data × 3)
   - Assumes consistent performance throughout year
   - 假设全年表现一致

4. **Account Classification | 账户分类**: Based on Chinese financial statement structure
   - 损益表 format with standard account groupings
   - 损益表格式，标准账户分组

### Calculation Transparency | 计算透明度

**Prime Cost Ratio Calculation:**
```
Prime Cost = Food Cost + Beverage Cost + Labor Cost
          = ¥516,959 + ¥357,495
          = ¥874,454

Prime Cost Ratio = ¥874,454 / ¥1,459,161
                 = 59.9%

Benchmark: <60% ✅
```

**Net Profit Margin Calculation:**
```
Net Profit Margin = Net Profit / Total Revenue
                  = ¥267,234 / ¥1,459,161
                  = 18.3%

Industry Benchmark: 5-10% ⭐ Significantly Above!
```

---

**Disclaimer | 免责声明**: This analysis is based on the provided financial data and industry
benchmarks. Actual performance may vary based on specific circumstances, local market conditions,
and business strategies. This report is for informational purposes only and does not constitute
financial advice. Consult with qualified financial professionals for business decisions.

本分析基于提供的财务数据和行业基准。实际表现可能因具体情况、当地市场条件和业务策略而异。
本报告仅供参考，不构成财务建议。请咨询合格的财务专业人士以做出业务决策。
```

---

## Example 2: Quick Question - Food Cost Percentage

### User Request
```
What's my food cost percentage and is it healthy?
```

### Claude's Response
```markdown
Let me analyze your food cost percentage...

[Extracts food cost and food revenue from Excel]

## Food Cost Analysis | 食品成本分析

**Food Cost | 食品成本**: ¥516,959
**Food Revenue | 食品收入**: ¥1,459,161
**Food Cost Percentage | 食品成本率**: 35.4%

### Industry Benchmark Comparison | 行业基准对比

```
Healthy Range for Restaurants:
餐饮行业健康区间:

├── 28% ░░░░░░░░░░░░░░░░░░░░
├── 30% ████████░░░░░░░░░░░░ ← Ideal 理想
├── 33% ████████████████░░░░
└── 35% ████████████████████ ← Your Cost 您的成本 (35.4%)
```

### Assessment | 评估

⚠️ **At Upper Limit** - Your food cost of 35.4% is at the upper boundary of the healthy range
(28-35%). While still acceptable, there's opportunity to improve.

⚠️ **处于上限** - 您的食品成本率35.4%处于健康区间（28-35%）的上边界。虽然仍可接受，但有改进空间。

### Quick Recommendation | 快速建议

**Opportunity**: Reducing food cost to 32% (midpoint) could save approximately **¥50,000** over
4 months with minimal impact on quality.

**机会**: 将食品成本率降至32%（中点）可在4个月内节省约**¥50,000**，对质量影响极小。

**Action Steps | 行动步骤**:
1. Review portion sizes for consistency
2. Negotiate with key suppliers
3. Analyze waste and spoilage

1. 检查份量是否一致
2. 与主要供应商谈判
3. 分析浪费和损耗
```

---

## Example 3: Trend Analysis Across Multiple Periods

### User Request
```
How is my profitability trending over the past 4 months?
```

### Claude's Response
```markdown
## Profitability Trend Analysis | 盈利能力趋势分析

[Extracts multi-period data]

### Monthly Trend | 月度趋势

| Month | 月份 | Revenue | 收入 | Net Profit | 净利润 | Net Margin | 净利润率 |
|-------|------|---------|------|------------|--------|------------|---------|
| May | 5月 | ¥346,725 | ¥346,725 | ¥63,000 | ¥63,000 | 18.2% | 18.2% |
| June | 6月 | ¥362,890 | ¥362,890 | ¥66,500 | ¥66,500 | 18.3% | 18.3% |
| July | 7月 | ¥374,112 | ¥374,112 | ¥68,800 | ¥68,800 | 18.4% | 18.4% |
| August | 8月 | ¥375,434 | ¥375,434 | ¥68,934 | ¥68,934 | 18.4% | 18.4% |

### Visual Trend | 可视化趋势

```
Revenue Growth:
收入增长:
¥350K ███████████████░░░░░░░░ May
¥363K ████████████████░░░░░░░ June
¥374K █████████████████░░░░░░ July
¥375K █████████████████░░░░░░ August (+8.3% total)

Net Profit Margin:
净利润率:
18.2% ████████████████████░░░░░░ May
18.3% ████████████████████░░░░░░ June
18.4% ████████████████████░░░░░░ July
18.4% ████████████████████░░░░░░ August (Stable & Excellent)
```

### Trend Insights | 趋势洞察

✅ **Positive Findings | 积极发现**:
1. **Consistent Growth** - Revenue increasing every month (+8.3% May to August)
2. **Stable Margins** - Net profit margin holding steady at ~18.3-18.4%
3. **Scaling Efficiency** - Revenue growing while maintaining margins (good cost control)

1. **持续增长** - 收入每月递增（5月至8月增长8.3%）
2. **利润率稳定** - 净利润率稳定在~18.3-18.4%
3. **规模效率** - 收入增长同时保持利润率（良好的成本控制）

### Interpretation | 解读

This is **excellent performance**:
- Revenue growth without margin sacrifice
- Operating leverage working in your favor (fixed costs spreading over higher sales)
- Indicates sustainable business model

这是**优秀的表现**:
- 收入增长而不牺牲利润率
- 经营杠杆对您有利（固定成本分摊到更高销售额）
- 表明业务模式可持续

### Forward-Looking Recommendation | 前瞻性建议

**Continue Current Strategy** - Your current operations are working well. Focus on:
1. Maintaining service quality as you scale
2. Capturing seasonality trends (if applicable)
3. Planning for next growth phase once you hit capacity

**继续当前策略** - 您当前的运营效果良好。重点关注：
1. 在规模扩大时保持服务质量
2. 把握季节性趋势（如适用）
3. 在达到产能上限后规划下一增长阶段
```

---

## Example 4: Industry Benchmarking Request

### User Request
```
How does my restaurant compare to industry standards?
```

### Claude's Response
```markdown
## Industry Benchmarking Report | 行业对标报告

**Your Business Type | 您的业务类型**: Restaurant (Full-Service)
**Industry Category | 行业类别**: Food & Beverage / 餐饮业
**Benchmarks Source | 基准来源**: China restaurant industry standards

---

### Performance Scorecard | 绩效评分卡

| Metric | 指标 | Your Business | 您的业务 | Industry Standard | 行业标准 | Score | 评分 | Status | 状态 |
|--------|------|---------------|----------|-------------------|----------|-------|------|--------|------|
| Net Profit Margin | 净利润率 | 18.3% | 18.3% | 5-10% | 5-10% | ★★★★★ | ★★★★★ | Well Above | 远超 |
| Prime Cost Ratio | 综合成本率 | 59.9% | 59.9% | <60% | <60% | ★★★★☆ | ★★★★☆ | At Target | 达标 |
| Food Cost % | 食品成本率 | 35.4% | 35.4% | 28-35% | 28-35% | ★★★☆☆ | ★★★☆☆ | Upper Limit | 上限 |
| Labor Cost % | 人工成本率 | 24.5% | 24.5% | 25-35% | 25-35% | ★★★★★ | ★★★★★ | Excellent | 优秀 |
| Rent % | 租金占比 | 6.6% | 6.6% | 5-10% | 5-10% | ★★★★☆ | ★★★★☆ | Good | 良好 |
| Operating Expense % | 营业费用率 | 21.7% | 21.7% | 15-25% | 15-25% | ★★★★☆ | ★★★★☆ | In Range | 在区间内 |

---

### Overall Performance Grade | 总体表现等级

```
    ⭐⭐⭐⭐⭐
    EXCELLENT
    优秀

Your restaurant ranks in the TOP 10% of restaurants for profitability.
您的餐厅盈利能力排名餐饮行业前10%。
```

---

### Competitive Position | 竞争地位

**Strengths vs Competition | vs 竞争对手的优势:**
1. **Exceptional Profitability** - 18.3% vs industry 7.5% average
   - 卓越的盈利能力 - 18.3% vs 行业平均7.5%
2. **Labor Efficiency** - 24.5% labor cost (below industry average)
   - 人工效率 - 24.5%人工成本（低于行业平均）
3. **Cost Control** - Well-managed operating expenses
   - 成本控制 - 营业费用管理良好

**Areas for Improvement | 改进空间:**
1. **Food Cost** - Currently at upper limit, opportunity to optimize
   - 食品成本 - 目前处于上限，有优化机会

---

### Market Positioning | 市场定位

Based on your financial profile, you appear to be:
- **Premium/Mid-Premium** positioning
- Strong operational execution
- Effective cost management
- High customer willingness to pay

根据您的财务状况，您似乎是：
- **高端/中高端**定位
- 运营执行力强
- 成本管理有效
- 客户支付意愿高

**Recommendation | 建议**: Maintain premium positioning and focus on quality consistency.
**建议**: 保持高端定位，注重质量一致性。
```

---

## Platform-Specific Notes

### On Claude Code
- Skill automatically loads when analyzing Excel files in project directory
- Full file system access for reading financial data
- Can reference files with `@filename.xlsx` syntax

### On Claude.ai
- Upload Excel file via attachment
- Skill activates when financial analysis requested
- May need to explicitly mention "financial analysis" if file name is ambiguous

### On Claude API
- Pass file as base64 or provide file path
- Skill invoked automatically via skill_id parameter
- Returns structured analysis in response

---

## Tips for Best Results

### 1. File Naming
Use descriptive names that indicate content:
- ✅ Good: `restaurant_financial_june_2024.xlsx`
- ✅ Good: `company_income_statement_q3.xlsx`
- ❌ Poor: `data.xlsx`, `file1.xlsx`

### 2. Provide Context
Help Claude understand your specific situation:
```
"Analyze @report.xlsx - this is a restaurant in Chengdu (tier 2 city),
operating for 6 months in the mid-premium segment"
```

### 3. Ask Follow-up Questions
The skill supports multi-turn conversations:
```
Turn 1: "Analyze my financial report"
Turn 2: "What's driving my high profitability?"
Turn 3: "Should I expand to delivery services?"
```

### 4. Specify Preferences
Tell Claude what you need:
```
"Analyze @report.xlsx with:
- Chinese language output only
- Focus on cost optimization opportunities
- Compare to retail industry benchmarks (not restaurant)"
```

---

## Troubleshooting

### Issue: Skill not activating
**Solution**: Explicitly mention "financial analysis" in your request

### Issue: Wrong industry benchmarks applied
**Solution**: Specify your industry: "Compare against retail benchmarks"

### Issue: Incorrect calculations
**Solution**: Check if account structure was validated. Ask: "Can you show me the account hierarchy you identified?"

### Issue: Missing bilingual output
**Solution**: Request explicitly: "Please provide analysis in both English and Chinese"

---

**Last Updated**: November 21, 2025
**Skill Version**: 1.0
**For Questions**: Refer to SKILL.md for detailed instructions
