import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="What does this project do? Answer in two sentences.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            cwd="C:\\projects\\pitwall",
        ),
    ):
        print(type(message).__name__)          # watch the loop's anatomy
        if hasattr(message, "result"):
            print("\n" + message.result)

asyncio.run(main())