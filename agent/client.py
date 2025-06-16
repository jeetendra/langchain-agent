import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient, StdioConnection

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""
from mcp.config import mcp_config

async def initilize_chat_model():
    try:
        print ("Initializing MCP Client...")
        mcp_client = MultiServerMCPClient(mcp_config["mcpServers"])

        tools = await mcp_client.get_tools()
        print("Available tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
    
        chat_model = init_chat_model(
            model="gpt-4o-mini",
        ).bind_tools(tools=tools)
        return chat_model
    except Exception as e:
        print(f"Error initializing chat model: {e}")
        raise

async def main():
    try:
        chat_model = await initilize_chat_model()
        if not chat_model:
            print("Chat model initialization failed.")
            return
        print("Welcome to the LangGraph Agent Client!")
        print("Type 'quit' or 'exit' to stop the client.")
        print("You can start typing your messages below:")
        while True:
            user_input = input("You: ")
            if user_input in ["quit", "exit"]:
                break

            ai_response = chat_model.invoke([{"role": "user", "content": user_input}])
            if not ai_response or not ai_response.content:
                print("AI: No response received.")
                print(ai_response) 
                continue
            print(f"AI: {ai_response.content}")
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())