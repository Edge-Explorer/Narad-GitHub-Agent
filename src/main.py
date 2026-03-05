import sys
import asyncio
from narad_mcp.server import mcp

def run_server():
    """Runs the MCP Server (Stdio mode)"""
    mcp.run()

async def run_cli():
    """Runs the Interactive CLI Agent"""
    from narad_mcp.cli import NaradCLI
    cli = NaradCLI()
    await cli.run()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        asyncio.run(run_cli())
    else:
        # Default to server mode
        run_server()
