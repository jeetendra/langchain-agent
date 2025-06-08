import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""

gpt4o_mini = init_chat_model(
    model="gpt-4o-mini",
)