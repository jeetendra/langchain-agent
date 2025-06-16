from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""

chat_model = init_chat_model(
    model="gpt-4o-mini",
)

async def main():
    print("Welcome to the LangGraph Agent Client!")
    print("Type 'quit' or 'exit' to stop the client.")
    print("You can start typing your messages below:")
    while True:
        user_input = input("You: ")
        if user_input in ["quit", "exit"]:
            break

        ai_response =get_response(user_input)

        print(f"AI: {ai_response}")

def get_response(user_input):
    
    response = chat_model.invoke([{"role": "user", "content": user_input}])
    return str(response.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())