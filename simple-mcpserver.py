import logging
import sys
from mcp.server.fastmcp import FastMCP

# --- Setup Enhanced Logging ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("mcp-server")

mcp = FastMCP("AdvancedNetworkServer")

# --- 1. TOOLS (The 'Verbs' - Do things) ---


@mcp.tool()
def calculate_growth(initial_value: float, rate: float, years: int) -> str:
    """Calculates compound growth over time."""
    logger.info(
        f"🚀 TOOL CALL: calculate_growth(val={initial_value}, rate={rate}, yrs={years})")
    final = initial_value * (1 + rate) ** years
    return f"The projected value after {years} years is {final:.2f}"

# --- 2. RESOURCES (The 'Nouns' - Data to read) ---


@mcp.resource("system://status")
def get_system_status() -> str:
    """Provides real-time server health and status."""
    logger.info("📂 RESOURCE ACCESS: system://status")
    return "Status: Operational | Load: Low | Network: Stable"

# --- 3. PROMPTS (The 'Templates' - Pre-set instructions) ---


@mcp.prompt()
def code_reviewer(code: str) -> str:
    """Creates a structured prompt for reviewing code snippets."""
    logger.info("📝 PROMPT GENERATION: code_reviewer")
    return f"Please review the following code for security and performance:\n\n{code}"


if __name__ == "__main__":
    logger.info("Starting Advanced MCP Server on SSE...")
    mcp.run(transport="sse")
