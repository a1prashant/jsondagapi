import asyncio
import logging
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-client")


async def run_full_diagnostic():
    uri = "http://localhost:8000/sse"

    logger.info(f"Connecting to {uri}...")
    async with sse_client(uri) as (reader, writer):
        async with ClientSession(reader, writer) as session:

            # --- PHASE 1: Initialization ---
            logger.info("Handshake: Initializing Session...")
            await session.initialize()

            # --- PHASE 2: Discovery (Stabilized) ---
            logger.info("Discovery: Listing available features...")

            # Instead of firing all at once, we add a tiny delay
            # or run them sequentially to avoid TaskGroup race conditions
            tools = await session.list_tools()
            await asyncio.sleep(0.1)  # Give the SSE stream a moment to breathe

            resources = await session.list_resources()
            await asyncio.sleep(0.1)

            prompts = await session.list_prompts()

            logger.info(
                f"Found {len(tools.tools)} tools, {len(resources.resources)} resources.")

            # --- PHASE 3: Execution (Tool) ---
            logger.info("Execution: Calling 'calculate_growth'...")
            tool_result = await session.call_tool(
                "calculate_growth",
                arguments={"initial_value": 1000, "rate": 0.05, "years": 10}
            )
            print(f"\n[TOOL RESULT]: {tool_result.content[0].text}\n")

            # --- PHASE 4: Data Retrieval (Resource) ---
            logger.info("Retrieval: Reading 'system://status'...")
            resource_result = await session.read_resource("system://status")
            print(f"[RESOURCE DATA]: {resource_result}\n")

            # --- PHASE 5: Template Generation (Prompt) ---
            logger.info("Template: Getting 'code_reviewer' prompt...")
            prompt_result = await session.get_prompt("code_reviewer", arguments={"code": "print('hello')"})
            print(f"[PROMPT TEXT]: {prompt_result.messages[0].content.text}\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_full_diagnostic())
    except Exception as e:
        logger.error(f"Diagnostic failed: {e}")
