from langchain.chat_models import init_chat_model

client = init_chat_model(
    model="ai/smollm2",
    base_url="http://localhost:12434/engines/v1",
    api_key="docker",
    model_provider="openai",
)

client_response = client.invoke(
    [{"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "write a small poem about the sea"}]
)

print(client_response.content)