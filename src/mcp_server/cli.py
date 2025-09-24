#!/usr/bin/env python3
"""CLI for Restaurant Financial MCP Server"""

import click
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional


@click.group()
def main():
    """Restaurant Financial Analysis MCP Server - Intelligent Chinese restaurant report analysis"""
    pass


@main.command()
@click.option(
    '--transport',
    default='stdio',
    type=click.Choice(['stdio', 'http']),
    help='Transport type: stdio for Claude Desktop, http for web/Cloudflare'
)
@click.option(
    '--port',
    default=8000,
    type=int,
    help='Port for HTTP transport (default: 8000)'
)
@click.option(
    '--host',
    default='localhost',
    type=str,
    help='Host for HTTP transport (default: localhost)'
)
def start_server(transport: str, port: int, host: str):
    """Start the MCP server for restaurant financial analysis"""

    if transport == 'stdio':
        asyncio.run(run_stdio())
    else:
        click.echo(f"🌐 HTTP transport will be available in next release")
        click.echo(f"   For now, use: restaurant-mcp start-server --transport stdio")
        sys.exit(1)


@main.command()
@click.option('--auto', is_flag=True, help='Automatically write config (recommended)')
def setup_claude(auto: bool):
    """Automatically configure Claude Desktop to use this MCP server"""

    click.echo("🔧 Setting up Claude Desktop configuration...")

    # Common Claude config locations
    possible_config_paths = [
        Path.home() / ".claude" / "mcp.json",
        Path.home() / "Library" / "Application Support" / "Claude" / "mcp.json",
        Path.home() / ".config" / "claude" / "mcp.json",
    ]

    mcp_config = {
        "type": "stdio",
        "command": "restaurant-mcp",
        "args": ["start-server", "--transport", "stdio"]
    }

    # Try to auto-configure if --auto flag or if we can find existing config
    config_path = None
    for path in possible_config_paths:
        if path.exists():
            config_path = path
            break

    # If no config exists, create in default location
    if not config_path and auto:
        config_path = Path.home() / ".claude" / "mcp.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

    if auto or config_path:
        try:
            # Load existing config or create new
            if config_path and config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    if "mcpServers" not in config:
                        config["mcpServers"] = {}
            else:
                config = {"mcpServers": {}}

            # Add our server
            config["mcpServers"]["fin-report-agent"] = mcp_config

            # Write config
            if config_path:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)

                click.echo(f"✅ Successfully configured Claude Desktop!")
                click.echo(f"   Config file: {config_path}")
                click.echo(f"   MCP server: fin-report-agent")
                click.echo("\n🔄 Please restart Claude Desktop to activate the MCP server")
                return
        except Exception as e:
            click.echo(f"⚠️  Auto-configuration failed: {e}")
            click.echo("📋 Falling back to manual instructions...\n")

    # Manual instructions
    config_content = {
        "mcpServers": {
            "fin-report-agent": mcp_config
        }
    }

    click.echo("\n📋 Add this to your Claude Desktop MCP configuration:")
    click.echo(json.dumps(config_content, indent=2))
    click.echo("\n💡 Config file locations (choose one):")
    for path in possible_config_paths:
        exists = "✓ exists" if path.exists() else ""
        click.echo(f"   - {path} {exists}")
    click.echo("\n💡 Tip: Run with --auto flag to configure automatically:")
    click.echo("   restaurant-mcp setup-claude --auto")
    click.echo("\n✅ After adding, restart Claude Desktop to activate the MCP server")


@main.command()
def test():
    """Test that the MCP server and tools are working"""

    click.echo("🧪 Testing MCP server components...")

    try:
        from .simple_tools import (
            get_excel_info,
            show_excel_visual,
            search_in_excel,
            read_excel_region,
            calculate
        )
        click.echo("✅ Simple tools imported successfully")

        from .server import RestaurantFinancialMCPServer
        click.echo("✅ MCP server class loaded")

        from .config import MCPServerConfig
        config = MCPServerConfig()
        click.echo(f"✅ Server config: {config.server_name} v{config.server_version}")

        click.echo("\n🎉 All components working correctly!")
        click.echo("\n💡 Next steps:")
        click.echo("   1. Run: restaurant-mcp setup-claude")
        click.echo("   2. Restart Claude Desktop")
        click.echo("   3. Ask Claude to analyze your restaurant Excel file")

    except Exception as e:
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


async def run_stdio():
    """Run MCP server in stdio mode for Claude Desktop"""

    # Add src to path for imports
    src_path = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(src_path))

    from mcp import stdio_server
    from .server import RestaurantFinancialMCPServer
    from .config import MCPServerConfig

    # Create configuration
    config = MCPServerConfig(
        server_name="fin-report-agent",
        server_version="1.0.0",
        enable_bilingual_output=True,
        log_level="INFO"
    )

    # Initialize server
    mcp_server = RestaurantFinancialMCPServer(config)

    # Run with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.get_server().run(
            read_stream,
            write_stream,
            mcp_server.get_server().create_initialization_options()
        )


if __name__ == "__main__":
    main()