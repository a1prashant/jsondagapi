import logging
import sys
from mcp.server.fastmcp import FastMCP, Context

# --- Setup Enhanced Logging ---
# We use stderr so logs don't interfere with the transport stream
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("mcp-master-server")

# Initialize FastMCP
mcp = FastMCP("UltimateMasterServer")

# --- 1. TOOLS (Model-Controlled Actions) ---


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Adds two integers. Use this for basic arithmetic."""
    logger.info(f"EXECUTION: add_numbers({a}, {b})")
    return a + b


@mcp.tool()
async def multiply_numbers(a: int, b: int) -> int:
    """Multiplies two numbers. Implemented as an async tool."""
    logger.info(f"EXECUTION: multiply_numbers({a}, {b})")
    return a * b


@mcp.tool()
async def summarize_data(text: str, ctx: Context) -> str:
    """
    SAMPLING: Asks the connected LLM to summarize the provided text.
    This demonstrates the server calling back to the client.
    """
    logger.info("SAMPLING: Requesting summary from client LLM...")
    try:
        # ctx.sample() is the official way to delegate work to the host LLM
        result = await ctx.sample(
            f"Please summarize this data concisely:\n\n{text}",
            max_tokens=100
        )
        return f"Summary produced via Sampling: {result.text}"
    except Exception as e:
        logger.error(f"Sampling failed: {e}")
        return f"Error: Could not perform sampling. Ensure client supports it. ({e})"

# --- 2. RESOURCES (Application-Controlled Data) ---


@mcp.resource("system://status")
def get_system_status() -> str:
    """Read-only resource providing server health information."""
    logger.info("RESOURCE ACCESS: system://status")
    return "Status: Operational | Transport: SSE | Version: 1.0.0"


@mcp.resource("config://app-settings")
def get_settings() -> dict:
    """Exposes application settings as a JSON resource."""
    return {
        "precision": 2,
        "timeout": 30,
        "environment": "development"
    }

# --- 3. PROMPTS (User-Invoked Templates) ---


@mcp.prompt()
def code_reviewer(code: str) -> str:
    """A prompt template that guides the LLM to perform a code review."""
    logger.info("PROMPT INVOKED: code_reviewer")
    return (
        "You are an expert Senior Software Engineer. Review the following code "
        "for security vulnerabilities and performance bottlenecks:\n\n"
        f"{code}"
    )

# --- 4. LIFECYCLE & EXECUTION ---


if __name__ == "__main__":
    logger.info("Starting Master MCP Server on SSE transport...")
    # Note: Using transport="sse" for network-based application as requested
    mcp.run(transport="sse")
