from agent import memory_agent
from google.adk.runners import Runner

from dotenv import load_dotenv
import asyncio

load_dotenv()

runner = Runner()

async def main_async():
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye!")
            break

        # Run the memory_agent with the user input
        response = await runner.run(memory_agent, user_input)

        print(f"🤖 Assistant: {response}")

if __name__ == "__main__":
    asyncio.run(main_async())
