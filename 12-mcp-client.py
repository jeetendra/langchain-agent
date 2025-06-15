from langchain_mcp_adapters.client import MultiServerMCPClient, Connection
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""
async def main ():
    
    # Initialize the chat model
    chat_model = init_chat_model(
        model="gpt-4o-mini",
    )

    # Initialize the MCP client with multiple servers
    mcp_client = MultiServerMCPClient(
        {
            "calculator": {
                "command": "python",
                "args": [".\mcp-server\calculator.py"],
                "transport": "stdio"
            },
            "weather": {
                "url": "http://localhost:8000/mcp",  # Ensure server is running here
                "transport": "streamable_http",
            }
        }
    )

    tools = await mcp_client.get_tools()
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")


    # Create a React agent with the chat model and tools
    react_agent = create_react_agent(
        model=chat_model,
        tools=tools,
    )

    response = await react_agent.ainvoke({"messages": [
        {"role": "user", "content": "What is 5 + 3 * 5?"},
        {"role": "user", "content": "What is the weather in New Delhi?"}
    ]})

    print("Response from React Agent:")
    for message in response["messages"]:
        print(f"{message.type}: {message.content}")

if __name__ == "__main__":
    asyncio.run(main()) 