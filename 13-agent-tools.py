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
from langchain_tavily.tavily_search import  TavilySearch

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY") or ""

tools = [
    TavilySearch().as_tool(),
]

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

result = graph.invoke({"messages": [HumanMessage(content="What is the latest news about GenAI?")]})
print(result["messages"][-1].content)