import asyncio
import logging
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from mcp.types import ClientCapabilities, TextContent, CreateMessageResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-client")


async def handle_sampling(params):
    return CreateMessageResult(
        role="assistant",
        content=TextContent(
            type="text", text="The data suggests a trend of success."),
        model="mock-gpt-4"
    )


async def run_client():
    uri = "http://127.0.0.1:8000/sse"
    # Note the object name here
    my_caps = ClientCapabilities(sampling={})

    logger.info("Connecting to Server via SSE...")

    async with sse_client(uri) as (reader, writer):
        # Using the sampling_callback for our AI summary tool
        async with ClientSession(reader, writer, sampling_callback=handle_sampling) as session:

            await asyncio.sleep(1.0)  # Stability warm-up

            # --- PHASE 1: Fixed Initialization ---
            try:
                logger.info("Initializing Handshake...")
                # The argument must be 'client_capabilities'
                await session.initialize()
                logger.info("✅ Connection Fully Established")
            except Exception as e:
                logger.error(f"Failed during initialization: {e}")
                return

            # --- PHASE 2: Comprehensive Feature Tests ---

            # 1. Test: Basic Addition
            logger.info("Testing 'add_numbers'...")
            res_add = await session.call_tool("add_numbers", {"a": 25, "b": 75})
            print(f"   👉 Add Result: {res_add.content[0].text}")

            # 2. Test: Async Multiplication
            logger.info("Testing 'multiply_numbers'...")
            res_mult = await session.call_tool("multiply_numbers", {"a": 12, "b": 12})
            print(f"   👉 Multiply Result: {res_mult.content[0].text}")

            # 3. Test: Sampling (The Server-to-Client callback)
            logger.info("Testing 'ai_summary'...")
            res_sum = await session.call_tool("ai_summary", {"text": "Network logs show 200 OK."})
            print(f"   👉 AI Summary Result: {res_sum.content[0].text}")

            # 4. Test: Resources
            logger.info("Reading status resource...")
            res_status = await session.read_resource("system://status")
            print(f"   👉 Resource Data: {res_status}")

            logger.info("All tests completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except Exception as e:
        logger.error(f"Fatal Client Error: {e}")
