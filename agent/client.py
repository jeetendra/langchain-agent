async def main():
    print("Welcome to the LangGraph Agent Client!")
    print("Type 'quit' or 'exit' to stop the client.")
    print("You can start typing your messages below:")
    while True:
        user_input = input("You: ")
        if user_input in ["quit", "exit"]:
            break

        print(f"AI: {user_input.capitalize()}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())