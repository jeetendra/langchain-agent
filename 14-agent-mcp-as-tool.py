import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient, Connection
from langchain_mcp_adapters.sessions import StdioConnection
import asyncio


load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""
MCP_FILESYSTEM_DIR = os.getenv("MCP_FILESYSTEM_DIR") or ""

connection = {
    "transport": 'stdio',
    "command": "npx", 
    "args": ["-y", "@modelcontextprotocol/server-filesystem", MCP_FILESYSTEM_DIR],
    # "env": None,
    # "cwd" : None,
    # "encoding_error_handler" : "strict",
    # "session_kwargs" : None,
    # "encoding": 
}

async def main():
    # TODO: fix types issue 
    mcp_client = MultiServerMCPClient({
        "filesystem": connection
    })
    tools = await mcp_client.get_tools()

    # print(tools)

    llm = init_chat_model(
        model="gpt-4o-mini",
    )

    llm_with_tools = llm.bind_tools(tools=tools)

    class State(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

    def chat(state: State) -> State:
        return {"messages":[llm_with_tools.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("assistant", chat)
    builder.add_node("tools", ToolNode(tools=tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    builder.add_edge("assistant", END)

    graph = builder.compile()

    result = await graph.ainvoke({"messages": [HumanMessage(content="show content from 1-localllm.py")]})
    
    print(result)
    print("#"*50)
    print(result["messages"][-1].content)

if __name__=="__main__":
    asyncio.run(main())