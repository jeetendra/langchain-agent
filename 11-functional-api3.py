from langgraph.func import entrypoint, task
from langchain.chat_models import init_chat_model
import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'project_manager_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""

@dataclass
class TaskResult:
    """Container for task results with error handling."""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None


@task
def createPRD(topic: str) -> TaskResult:
    """Create PRD document for a given topic with error handling."""
    try:
        logging.info(f"Creating PRD for topic: {topic}")
        if not topic.strip():
            raise ValueError("Topic ca" \
            "nnot be empty")

        chat_model = init_chat_model(model="gpt-4o-mini")
        response = chat_model.invoke(
            [{"role": "user", "content": f"Create a PRD document for {topic}."}]
        )
        
        result = str(response.content)
        logging.info("Successfully created PRD")
        return TaskResult(success=True, content=result)

    except Exception as e:
        error_msg = f"Error creating PRD: {str(e)}"
        logging.error(error_msg)
        return TaskResult(success=False, error=error_msg)

@task
def createTask(prd: str) -> TaskResult:
    """Create a task list based on the PRD document with error handling."""
    try:
        logging.info("Creating task list from PRD")
        if not prd.strip():
            raise ValueError("PRD cannot be empty")

        chat_model = init_chat_model(model="gpt-4o-mini")
        response = chat_model.invoke(
            [{"role": "user", "content": f"Create a task list based on the following PRD: {prd}"}]
        )
        
        result = str(response.content)
        logging.info("Successfully created task list")
        return TaskResult(success=True, content=result)

    except Exception as e:
        error_msg = f"Error creating task list: {str(e)}"
        logging.error(error_msg)
        return TaskResult(success=False, error=error_msg)

@entrypoint()
def projectManager(topic: str) -> Dict[str, Any]:
    """Project manager workflow that creates a PRD and task list for a given topic with error handling."""
    try:
        logging.info(f"Starting project manager workflow for topic: {topic}")
        
        # Create PRD
        prd_result = createPRD(topic).result()
        if not prd_result.success:
            return {
                "success": False,
                "error": prd_result.error,
                "stage": "PRD Creation"
            }
        
        # Create Task List
        task_result = createTask(prd_result.content).result()
        if not task_result.success:
            return {
                "success": False,
                "error": task_result.error,
                "stage": "Task List Creation"
            }
        
        # Success case
        logging.info("Successfully completed project manager workflow")
        return {
            "success": True,
            "prd": prd_result.content,
            "task_list": task_result.content
        }

    except Exception as e:
        error_msg = f"Unexpected error in project manager workflow: {str(e)}"
        logging.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "stage": "Workflow"
        }

def main():
    # Test cases
    test_topics = [
        "todo app",
        "",  # Should trigger validation error
        "complex enterprise resource planning system"
    ]

    for topic in test_topics:
        print(f"\n{'='*50}\nProcessing topic: {topic}\n{'='*50}")
        result = projectManager.invoke(topic)
        
        if result["success"]:
            print("\nProject Manager Result:")
            print("\nPRD:")
            print(result["prd"])
            print("\nTask List:")
            print(result["task_list"])
        else:
            print(f"\nError in {result['stage']}:")
            print(result["error"])

if __name__ == "__main__":
    main()