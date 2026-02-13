import asyncio
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


async def main():
    uri = "http://127.0.0.1:8000/sse"

    print(f"Connecting to {uri}...")

    async with sse_client(uri) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # 1. Initialize
            await session.initialize()

            # 2. Call the 'add' tool
            result = await session.call_tool("add", {"a": 10, "b": 20})
            print(f"✅ Tool Result: {result.content[0].text}")

            # 3. Read the resource
            resource = await session.read_resource("echo://hello_world")

            # FIX: It is '.contents' (with an 's') in the MCP SDK
            if resource.contents:
                # The first item in contents is usually TextResourceContents
                print(f"✅ Resource Result: {resource.contents[0].text}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error: {e}")
