
from pydantic import BaseModel 
from langgraph.graph import StateGraph, START, END

class State(BaseModel):
    sports_news: str = ""
    business_news: str = ""
    entertainment_news: str = ""
    gossips: str = ""
    final_news: str = ""

def sports_news(state: State):
    return {"sports_news": "todays sports news ..."}

def business_news(state: State):
    return {"business_news": "todays business news ..."}

def entertainment_news(state: State):
    return {"entertainment_news": "todays entertainment news ..."}

def gossip(state: State):
    return {"gossip": "todays top gossips ..."}

def final_node(state: State):
    return {"final_news" : "\n" + state.business_news + "\n" + state.entertainment_news + "\n" + state.sports_news + "\n" + state.gossips}

builder = StateGraph(State)

builder.add_node("sports", sports_news)
builder.add_node("business", business_news)
builder.add_node("entertainment", entertainment_news)
builder.add_node("gossip", gossip)
builder.add_node("final", final_node)

builder.add_edge(START, "sports")
builder.add_edge(START, "business")
builder.add_edge(START, "entertainment")
builder.add_edge(START, "gossip")

builder.add_edge(["sports", "business", "entertainment", "gossip"], "final")
builder.add_edge("final", END)

graph = builder.compile()

print(graph.get_graph().draw_ascii())

print("="*50)

print(graph.invoke({sports_news: "", entertainment_news: ""}))

