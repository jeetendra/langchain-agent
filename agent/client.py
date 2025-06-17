import os
import asyncio
from chat_graph import chat_graph

async def main():
    """Main application loop."""
    try:
        print("\nWelcome to the LangGraph Agent Client!")
        print("Type 'quit' or 'exit' to stop the client.")
        print("You can start typing your messages below:\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                    
                if user_input.lower() in ["quit", "exit"]:
                    print("\nGoodbye!")
                    break

                ai_response = await chat_graph(user_input)
                if not ai_response:
                    print("AI: No response received.")
                    continue
                print(f"\nAI: {ai_response}\n")
    
            except Exception as e:
                print(f"\nError processing message: {str(e)}\n")
                continue
                
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    asyncio.run(main())