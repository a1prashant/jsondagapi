from mcp.server.fastmcp import FastMCP

# Create a server instance
mcp = FastMCP("EasyServer")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """A resource that just repeats what you give it."""
    return f"Resource says: {message}"


if __name__ == "__main__":
    # We use SSE for the transport so it works over a network URL
    mcp.run(transport="sse")
