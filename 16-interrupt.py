from pydantic import BaseModel 
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

class State(BaseModel):
    message: str

def node1(state: State):
    print("Processing Node1")
    return {"message": state.message + " " + "node1"}

def node2(state: State):
    print("Processing Node2")
    return {"message": state.message + " " + "node2"}

def interrupt_node(state: State):
    print("Processing Interrupt")
    answer = interrupt("what is your age?")
    return {"message": state.message + " " + answer}


builder = StateGraph(State)
builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_node("interrupt_node", interrupt_node)

builder.add_edge(START, "node1")
builder.add_edge("node1", "interrupt_node")
builder.add_edge("interrupt_node", "node2")
builder.add_edge("node2", END)

checkpointer = MemorySaver()
config:RunnableConfig  = {
    "configurable": {
        "thread_id": "1",
    }
}
graph = builder.compile(checkpointer=checkpointer)

response = graph.invoke({"message": "hi"}, config=config)


print(response)
