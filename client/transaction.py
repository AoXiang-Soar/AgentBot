import asyncio

from mcp import ClientSession
from pydantic import AnyUrl


async def main(session: ClientSession):
    """
    Transaction logic main function, where logic like FSM can be executed.
    Should only be called by the MCP client.
    """
    # Do anything here. For example, call LLM.
    # asyncio.gather can execute multiple calls concurrently
    tools, result, resource, prompt = await asyncio.gather(
        session.list_tools(),
        session.call_tool("tool_demo", {'name': 'Test'}),
        session.read_resource(AnyUrl("file://utils.py")),
        session.get_prompt("prompt_demo")
    )

    print("Tools:")
    for tool in tools.tools:
        print('\tTool Name:', tool.name)
    print("Result:", result.content[0].text)
    print("Resource:", resource.contents[0].text)
    print("Prompt:", prompt.messages[0].content.text)