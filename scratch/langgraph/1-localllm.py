from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:12434/engines/v1",
    api_key="docker",
)

completion = client.chat.completions.create(
    model="ai/smollm2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke on programming?"}
    ]
)

print(completion.choices[0].message.content)