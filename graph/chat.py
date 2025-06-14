from pydantic import BaseModel
from langgraph.graph.message import add_messages
from typing import List, Annotated, TypedDict, Literal
from langgraph.graph import START, END, StateGraph

useLocalLLM = False
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
    response = llm.invoke(state["messages"])
    print(f"Assistant: {response.content}")

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


graph = StateGraph(AgentState)

graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", lambda state: state["next_state"], {
    "chat": "chat",
    "END": END
})

chat_graph = graph.compile()

