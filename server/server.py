from mcp.server.fastmcp import FastMCP


mcp = FastMCP("MCPServer")

@mcp.tool()
async def tool_demo(context: str) -> str:
    """A tool call demo"""
    return f"Client Says: {context}"

@mcp.prompt()
async def prompt_demo() -> str:
    """A prompt call demo"""
    return f"This is a prompt."

@mcp.resource('file://server.py')
async def resource_demo() -> str:
    """A resource call demo"""
    with open('./server/server.py', 'r', encoding='utf8') as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()