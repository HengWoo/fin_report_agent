# Cloudflare Deployment Guide

## How Serena Does It

Serena uses a clever approach to make installation easy:

### 1. **CLI Entry Points** (pyproject.toml)
```toml
[project.scripts]
serena = "serena.cli:top_level"
serena-mcp-server = "serena.cli:start_mcp_server"
```

This creates shell commands that users can run:
```bash
uvx --from git+https://github.com/oraios/serena serena start-mcp-server
```

### 2. **Cloudflare Tunnel for Public Access**
```bash
# Start local server
uvx mcpo --port 8000 --api-key <SECRET> -- \
  uvx --from git+https://github.com/oraios/serena \
  serena start-mcp-server --context chatgpt --project $(pwd)

# Expose via Cloudflare
cloudflared tunnel --url http://localhost:8000
```

This gives a public HTTPS URL like: `https://xxx.trycloudflare.com`

### 3. **Transport Options**
Serena supports multiple transports:
- `stdio` - Direct stdin/stdout (for Claude Desktop)
- `sse` - Server-Sent Events (for web)
- `streamable-http` - HTTP streaming (for ChatGPT)

---

## Our Restaurant Financial Agent - Deployment Options

### Option 1: Local Claude Desktop (Current - Simplest)

**How it works now:**
```json
// .mcp.json
{
  "mcpServers": {
    "restaurant-financial-analysis": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "run_mcp_server.py"]
    }
  }
}
```

**User installation:**
```bash
git clone <repo>
cd fin_report_agent
uv sync
# Claude Code auto-detects .mcp.json
```

### Option 2: Cloudflare Tunnel (Public Access)

**Setup CLI entry points** - Add to `pyproject.toml`:
```toml
[project.scripts]
fin-report-agent = "src.mcp_server.cli:main"
fin-report-agent-server = "src.mcp_server.cli:start_server"
```

**Create CLI module** - `src/mcp_server/cli.py`:
```python
import click
from .server import RestaurantFinancialMCPServer

@click.group()
def main():
    """Restaurant Financial Analysis MCP Server"""
    pass

@main.command()
@click.option('--transport', default='stdio',
              type=click.Choice(['stdio', 'sse', 'streamable-http']))
@click.option('--port', default=8000)
def start_server(transport, port):
    """Start the MCP server"""
    server = RestaurantFinancialMCPServer()
    if transport == 'stdio':
        # Current stdio mode
        asyncio.run(server.run_stdio())
    else:
        # HTTP mode for Cloudflare
        asyncio.run(server.run_http(port=port))
```

**User installation (one command):**
```bash
uvx --from git+https://github.com/yourusername/fin-report-agent \
  fin-report-agent start-server --transport streamable-http --port 8000
```

**Expose via Cloudflare:**
```bash
cloudflared tunnel --url http://localhost:8000
# Get URL: https://xxx.trycloudflare.com
```

### Option 3: Cloudflare Workers (Fully Hosted)

**Deploy as serverless function:**
```bash
# Install Wrangler
npm install -g wrangler

# Deploy
wrangler deploy
```

**Benefits:**
- No local installation needed
- Scales automatically
- Global CDN
- Free tier available

**Configuration** - `wrangler.toml`:
```toml
name = "fin-report-agent"
main = "src/worker.py"
compatibility_date = "2024-01-01"

[vars]
MCP_SERVER_NAME = "restaurant-financial-analysis"
```

---

## Recommended Approach for Our Agent

### Phase 1: Package with CLI (Like Serena)

**1. Update pyproject.toml:**
```toml
[project]
name = "fin-report-agent"
version = "0.1.0"
description = "Financial analysis MCP server for Chinese restaurant reports"

[project.scripts]
fin-report-agent = "src.mcp_server.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**2. Create CLI module:**
```python
# src/mcp_server/cli.py
import click
import asyncio
from .server import RestaurantFinancialMCPServer
from mcp import stdio_server

@click.command()
@click.option('--transport', default='stdio',
              type=click.Choice(['stdio', 'http']))
@click.option('--port', default=8000, help='Port for HTTP transport')
def main(transport, port):
    """Restaurant Financial Analysis MCP Server"""
    if transport == 'stdio':
        asyncio.run(run_stdio())
    else:
        asyncio.run(run_http(port))

async def run_stdio():
    server = RestaurantFinancialMCPServer()
    async with stdio_server() as (read_stream, write_stream):
        await server.get_server().run(
            read_stream, write_stream,
            server.get_server().create_initialization_options()
        )
```

**3. User installation becomes:**
```bash
# One command installation
uvx --from git+https://github.com/yourname/fin-report-agent fin-report-agent

# Or install and use
uv tool install git+https://github.com/yourname/fin-report-agent
fin-report-agent
```

### Phase 2: Add Cloudflare Tunnel Support

**For public access (optional):**
```bash
# Terminal 1: Start server with HTTP transport
uvx fin-report-agent --transport http --port 8000

# Terminal 2: Expose via Cloudflare
cloudflared tunnel --url http://localhost:8000
# Get: https://xxx.trycloudflare.com
```

**Use in ChatGPT Custom GPT:**
1. Add API with Bearer auth
2. Import schema from `https://xxx.trycloudflare.com/openapi.json`
3. ChatGPT can now use your financial analysis tools!

### Phase 3: Publish to PyPI

**Make it even easier:**
```bash
# Install from PyPI
pip install fin-report-agent

# Or with uvx
uvx fin-report-agent
```

**Users get:**
- One command installation
- Auto-updates
- Works anywhere Python is installed

---

## Implementation Checklist

### ✅ What We Have Now
- [x] Simple tools working
- [x] MCP server with stdio transport
- [x] .mcp.json for Claude Code
- [x] Documentation

### 🚀 Next Steps for Distribution

**Step 1: Add CLI Entry Point**
- [ ] Create `src/mcp_server/cli.py`
- [ ] Add `[project.scripts]` to `pyproject.toml`
- [ ] Test with `uv run fin-report-agent`

**Step 2: Add HTTP Transport**
- [ ] Implement HTTP server mode
- [ ] Add OpenAPI schema generation
- [ ] Test with curl/Postman

**Step 3: Cloudflare Integration**
- [ ] Document Cloudflare tunnel setup
- [ ] Add API key authentication
- [ ] Create ChatGPT integration guide

**Step 4: Publishing**
- [ ] Publish to PyPI
- [ ] Create GitHub releases
- [ ] Add to awesome-mcp list

---

## Benefits of Each Approach

### Local Installation (.mcp.json)
✅ **Pros:**
- Private/secure (no network)
- Fast (no latency)
- Simple setup

❌ **Cons:**
- Each user needs to install
- Local files only
- No sharing between users

### Cloudflare Tunnel (Public HTTP)
✅ **Pros:**
- Share one server with team
- Access from anywhere
- Works with ChatGPT
- No installation for end users

❌ **Cons:**
- Need to keep server running
- Security considerations (API keys)
- Network latency

### Cloudflare Workers (Serverless)
✅ **Pros:**
- No server to maintain
- Scales automatically
- Global distribution
- Free tier

❌ **Cons:**
- Cold start latency
- File upload limits
- More complex setup

---

## Recommended Path

**For your use case (restaurant financial analysis):**

1. **Start with:** Package with CLI (like Serena)
   - Easy installation: `uvx fin-report-agent`
   - Works with Claude Code immediately
   - Can add Cloudflare later

2. **Add later:** Cloudflare tunnel option
   - For teams who want shared access
   - For ChatGPT integration
   - Optional feature

3. **Consider:** PyPI publishing
   - When ready for public release
   - Makes it discoverable
   - Professional distribution

**Estimated effort:**
- CLI entry point: 1-2 hours
- HTTP transport: 2-4 hours
- Cloudflare tunnel: 1 hour
- PyPI publishing: 2-3 hours

**Total: 1-2 days of work for full distribution setup**

---

## Example: One-Command Installation

**Current (requires manual setup):**
```bash
git clone repo
cd fin_report_agent
uv sync
# Configure .mcp.json
```

**After implementing CLI:**
```bash
# Just this!
uvx --from git+https://github.com/you/fin-report-agent fin-report-agent
```

**After PyPI:**
```bash
# Even simpler!
uvx fin-report-agent
```

This is exactly how Serena achieves its one-command installation! 🚀