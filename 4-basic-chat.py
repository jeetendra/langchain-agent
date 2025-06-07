from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing import List, Annotated, TypedDict, Literal
from langgraph.graph import START, END, StateGraph
useLocalLLM = True

if useLocalLLM:
    from llms.llama_local import local_llama
    llm = local_llama
else:
    from llms.openai_gpt_4o import gpt4o_mini
    llm = gpt4o_mini

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    next_state: Literal["chat", "END"]
    
def chat_node(state: AgentState) -> AgentState:
    print("B4",state["messages"])
    response = llm.invoke(state["messages"])

    print(f"Assistant: {response.content}")

    # loop
    user_input = input("You: ")
    if user_input.lower() in ["bye", "exit"]:
        return {
            "messages": [response],
            "next_state": "END"
        }

    return {
        "messages": [response, {"role": "user", "content": user_input}],
        "next_state": "chat"
    }

def chat_condition(state: AgentState) -> str:
    if state["next_state"] == "END":
        return "END"
    return "chat"
graph = StateGraph(AgentState)

graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", chat_condition, {
    "chat": "chat",
    "END": END
})


app = graph.compile()

user_input = input("You: ")

initial_state = {
    "messages": [{"role": "user", "content": user_input}],
    "next_step": "chat"
}

final_state = app.invoke(initial_state)
