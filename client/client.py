from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .transaction import main

import os


current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
server_params = StdioServerParameters(
    command="python",
    args=[f'{project_root}/server/server.py'],
    env=None
)

async def run():
    """Start the MCP client. The local MCP server will be started by the client and maintain a long conversation."""
    # Connecting
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await main(session)