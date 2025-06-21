from typing import Literal
from pydantic import BaseModel 
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt, Interrupt
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

def node3(state: State):
    print("Processing Node3")
    return {"message": state.message + " " + "node3"}

def interrupt_node(state: State) -> Command[Literal["node2", "node3"]]:
    print("Processing Interrupt")
    answer = interrupt("Should i continue?")
    if answer:
        return Command(goto="node2")
    else:
        return Command(goto="node3")
        


builder = StateGraph(State)
builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_node("node3", node3)
builder.add_node("interrupt_node", interrupt_node)

builder.add_edge(START, "node1")
builder.add_edge("node1", "interrupt_node")
# builder.add_edge("interrupt_node", "node2") # user will decide
builder.add_edge("node2", "node3")
builder.add_edge("node3", END)

checkpointer = MemorySaver()
config:RunnableConfig  = {
    "configurable": {
        "thread_id": "1",
    }
}
graph = builder.compile(checkpointer=checkpointer)

response = graph.invoke({"message": "hi"}, config=config)


# print(response)

print(response["message"])
# print(type(response["__interrupt__"][0])) 
# print(response["__interrupt__"][0])
interrupted: Interrupt = response["__interrupt__"][0]
if interrupted and interrupted.resumable:
    print(interrupted.value)

command = Command(resume=False)
print(graph.invoke(command, config=config))