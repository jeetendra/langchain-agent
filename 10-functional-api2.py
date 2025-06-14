from langgraph.func import entrypoint, task
from langchain.chat_models import init_chat_model
import os
# Load environment variables
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""


@task
def createPRD(topic: str) -> str:
    """create PRD document for a given topic."""
    chat_model = init_chat_model(model="gpt-4o-mini")
    response = chat_model.invoke(
        [{"role": "user", "content": f"Create a PRD document for {topic}."}]
    )
    return str(response.content)

@task
def createTask(prd: str) -> str:
    """Create a task list based on the PRD document."""
    chat_model = init_chat_model(model="gpt-4o-mini")
    response = chat_model.invoke(
        [{"role": "user", "content": f"Create a task list based on the following PRD: {prd}"}]
    )
    return str(response.content)

@entrypoint()
def projectManager(topic: str) -> str:
    """Project manager workflow that creates a PRD and task list for a given topic."""
    prd = createPRD(topic).result()
    task_list = createTask(prd).result()
    return f"PRD: {prd}\nTask List: {task_list}"

result = projectManager.invoke("todo app")

print(f"Project Manager Result:\n{result}")