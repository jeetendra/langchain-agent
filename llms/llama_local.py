from langchain.chat_models import init_chat_model

local_llama = init_chat_model(
    model="llama3.2",
    base_url="http://localhost:11434/",
    api_key="docker",
    model_provider="ollama",
    temperature=1,
)