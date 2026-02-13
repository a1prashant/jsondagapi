

```
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
from datetime import datetime

# Create MCP server
mcp = FastMCP("Distributed Demo MCP")

# Define tools
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two integers"""
    return a * b

@mcp.tool()
def get_time() -> str:
    """Return server time"""
    return datetime.now().isoformat()


# FastAPI app
app = FastAPI()

# Mount MCP on HTTP
app.mount("/", mcp.asgi_app())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

```

```
import asyncio
from mcp.client.http import http_client
from mcp import ClientSession


async def main():
    async with http_client("http://127.0.0.1:8000") as (read, write):
        async with ClientSession(read, write) as session:
            
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print("-", tool.name)

            # Call add
            result = await session.call_tool(
                "add",
                arguments={"a": 10, "b": 20}
            )
            print("Add result:", result.content[0].text)

            # Call multiply
            result = await session.call_tool(
                "multiply",
                arguments={"a": 3, "b": 7}
            )
            print("Multiply result:", result.content[0].text)

            # Call get_time
            result = await session.call_tool("get_time")
            print("Time:", result.content[0].text)


asyncio.run(main())

```
