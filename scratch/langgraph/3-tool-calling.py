from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""

checkpointer = InMemorySaver()

class AgentOutput(BaseModel):
    
    result: str


useLocalLLM = True

if useLocalLLM:
    # llm = init_chat_model(
    #     model="ai/smollm2",
    #     base_url="http://localhost:12434/engines/v1",
    #     api_key="docker",
    #     model_provider="openai",
    # )

    llm = init_chat_model(
        model="llama3.2",
        base_url="http://localhost:11434/",
        api_key="docker",
        model_provider="ollama",
        temperature=1,
    )
else:
    llm = init_chat_model(
        model="gpt-4o-mini",
    )

def add(a: int, b: int) -> int:
    """Add two numbers."""
    print(f"Adding {a} and {b}")
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f"Multiplying {a} and {b}")
    return a * b

agent = create_react_agent(
    model=llm,
    prompt="You are a helpful assistant.",
    name="SimpleAgent",
    tools=[
        add, multiply
    ],
    checkpointer=checkpointer,
    # response_format=AgentOutput
)

config: RunnableConfig = {"recursion_limit": 10, "configurable": {"thread_id": "1"}}

response =  agent.invoke(
    {"messages": [{"role": "user", "content": "What is 2 + 3 * 6"}]},
    config=config
)

print("Agent response:")
print(response["messages"][-1].content)