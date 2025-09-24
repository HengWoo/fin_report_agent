# 🚀 Quick Start - One-Command Installation

## For Claude Code (Recommended)

From your project directory:

```bash
claude mcp add fin-report-agent -- uvx --from git+https://github.com/HengWoo/fin_report_agent fin-report-agent start-server --transport stdio
```

Then ask Claude to analyze your Excel file! 🎉

**Note:** Claude Code automatically adds this to your project's `.claude/mcp.json`

---

## For Claude Desktop

### Step 1: Install
```bash
uv tool install git+https://github.com/HengWoo/fin_report_agent
```

### Step 2: Auto-Configure
```bash
fin-report-agent setup-claude --auto
```

This **automatically writes** the configuration to Claude Desktop!

### Step 3: Restart Claude Desktop

### Step 4: Use It!
Ask Claude:
```
Claude，请分析 @my_restaurant_report.xlsx
```

That's it! 🎉

---

## Quick Comparison: Claude Code vs Claude Desktop

| Feature | Claude Code | Claude Desktop |
|---------|-------------|----------------|
| **Installation** | One command | Install + configure |
| **Setup** | `claude mcp add ...` | `fin-report-agent setup-claude --auto` |
| **Scope** | Per-project | Global |
| **Config file** | `.claude/mcp.json` (project) | `~/.claude/mcp.json` (global) |
| **Best for** | Developers, project work | General users, global access |

---

## What Changed?

### ✅ MCP Server Name
- **Old**: `restaurant-financial-analysis`
- **New**: `fin-report-agent`

### ✅ Auto-Configuration
- **Old**: Manual copy-paste of config
- **New**: Automatic with `--auto` flag

### ✅ Installation Flow

**Before (3 manual steps):**
```bash
# 1. Install
uv tool install git+...

# 2. Run setup (shows config)
fin-report-agent setup-claude

# 3. Manually edit ~/.claude/mcp.json
# (tedious!)
```

**After (2 steps, one automatic):**
```bash
# 1. Install
uv tool install git+https://github.com/HengWoo/fin_report_agent

# 2. Auto-configure
fin-report-agent setup-claude --auto
# ✨ Automatically writes config!

# 3. Restart Claude Desktop
```

---

## Configuration Details

### What Gets Written

Location: `~/.claude/mcp.json` (or appropriate location for your OS)

Content:
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

### Smart Configuration

The `setup-claude --auto` command:
1. ✅ Detects existing Claude config locations:
   - `~/.claude/mcp.json`
   - `~/Library/Application Support/Claude/mcp.json` (macOS)
   - `~/.config/claude/mcp.json` (Linux)

2. ✅ Loads existing config (if any)
3. ✅ Adds/updates `fin-report-agent` entry
4. ✅ Preserves other MCP servers
5. ✅ Creates directory if needed
6. ✅ Falls back to manual instructions if fails

---

## Troubleshooting

### Auto-config doesn't work?

**Option 1: Try without --auto**
```bash
fin-report-agent setup-claude
# Shows manual instructions
```

**Option 2: Manual configuration**
1. Find your Claude config file
2. Add the JSON config shown above
3. Restart Claude Desktop

### Verify installation
```bash
fin-report-agent test
```

Output should show:
```
🧪 Testing MCP server components...
✅ Simple tools imported successfully
✅ MCP server class loaded
✅ Server config: fin-report-agent v1.0.0
🎉 All components working correctly!
```

### Check where config was written
```bash
fin-report-agent setup-claude --auto
```

Look for output:
```
✅ Successfully configured Claude Desktop!
   Config file: /Users/you/.claude/mcp.json
   MCP server: fin-report-agent
```

---

## Complete Example

```bash
# Fresh installation on new machine

# 1. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install fin-report-agent MCP server
uv tool install git+https://github.com/HengWoo/fin_report_agent

# 3. Auto-configure Claude Desktop
fin-report-agent setup-claude --auto

# Output:
# 🔧 Setting up Claude Desktop configuration...
# ✅ Successfully configured Claude Desktop!
#    Config file: /Users/you/.claude/mcp.json
#    MCP server: fin-report-agent
# 🔄 Please restart Claude Desktop to activate the MCP server

# 4. Restart Claude Desktop

# 5. Use with Claude!
# Upload Excel file, ask Claude to analyze
```

**Total time: < 2 minutes** ⚡

---

## For Developers

### Local Development
```bash
# Clone repo
git clone https://github.com/HengWoo/fin_report_agent
cd fin_report_agent

# Install with uv
uv sync

# Run locally
uv run fin-report-agent test
uv run fin-report-agent start-server
```

### Build Package
```bash
# Build wheel
uv build

# Install from local build
uv tool install dist/*.whl
```

---

## Comparison with Other MCP Servers

| Feature | fin-report-agent | Typical MCP |
|---------|------------------|-------------|
| Installation | 1 command | Multiple steps |
| Configuration | Automatic | Manual |
| Setup time | < 2 minutes | 10+ minutes |
| User skill | Anyone | Developers |
| Documentation | Built-in | External |

---

## What Makes This Special?

### 🎯 Simple Tools + Claude Intelligence
- Only 150 lines of tool code
- Claude provides ALL the intelligence
- Transparent, explainable reasoning
- Works with ANY Excel format

### 🚀 Professional Distribution
- One-command installation
- Automatic configuration
- Proper versioning
- GitHub integration

### 💡 Real-World Success
- Prevented ¥124,274 calculation error
- Correctly identified ¥73,906.01 (not ¥198,180.28)
- Generated comprehensive bilingual analysis
- Identified ¥80,000/year savings opportunity

---

## Next Steps

### After Installation:
1. Try analyzing a sample Excel file
2. Read the documentation in README.md
3. Explore the 5 simple tools
4. Check out CLOUDFLARE_DEPLOYMENT.md for team usage

### For Advanced Users:
- HTTP transport for Cloudflare (coming soon)
- Custom context configurations
- Integration with ChatGPT
- API access for automation

---

**Built with Claude Code** - https://claude.ai/code