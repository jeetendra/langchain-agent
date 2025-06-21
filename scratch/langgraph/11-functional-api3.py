from langgraph.func import entrypoint, task
from langchain.chat_models import init_chat_model
import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
from graph.chat import chat_graph
def loadMD(filename: str) -> str:
    """Load the markdown file for the project manager."""
    try:
        if not filename or not filename.strip():
            raise ValueError("Filename is empty or None")
            
        # Convert relative path to absolute using the script's directory
        if not os.path.isabs(filename):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            abs_path = os.path.join(base_dir, filename)
        else:
            abs_path = filename
            
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {abs_path}")
            
        with open(abs_path, "r", encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                raise ValueError(f"File is empty: {filename}")
            logging.info(f"Successfully loaded markdown file: {filename}")
            return content
            
    except Exception as e:
        logging.error(f"Error loading markdown file {filename}: {str(e)}")
        return ""


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
            raise ValueError("Topic cannot be empty")        
        
        chat_model = init_chat_model(model="gpt-4o-mini")
        instruction_path = os.path.join(os.path.dirname(__file__), "instruction", "create-prd.mdc")
        instruction = loadMD(instruction_path)
        if not instruction:
            raise ValueError("Failed to load PRD instruction template")
        
        logging.info(f"Loaded PRD instruction template: {instruction[:100]}...")
        
        # Initial conversation messages
        messages = [
            {"role": "system", "content": "You are a professional project manager creating a PRD. Follow the template exactly and be thorough."},
            {"role": "user", "content": f"Using this template:\n\n{instruction}\n\nCreate a detailed PRD document for: {topic}"}
        ]
        initial_state = {
            "messages": messages,
            "next_step": "chat"
        }
        logging.info("Initialized chat graph with initial messages")
        output = chat_graph.invoke(initial_state)  # Initialize the chat graph with the messages
        logging.info("output from chat graph initialized", output)    


        # # First draft
        # response = chat_model.invoke(messages)
        # initial_prd = str(response.content)
        # logging.info("Created initial PRD draft")
        
        # logging.info("=" * 50)
        # logging.info(f"Initial PRD draft: {initial_prd}")
        # print(initial_prd)
        # suggestions = input("You: ")
        # # Enhancement iteration
        # messages.extend([
        #     {"role": "assistant", "content": initial_prd},
        #     {"role": "user", "content": suggestions}
        # ])
        
        # response = chat_model.invoke(messages)
        # enhanced_prd = str(response.content)
        # logging.info("Enhanced PRD with additional details")
        # logging.info("=" * 50)
        # logging.info(f"Enhanced PRD: {enhanced_prd}")       
        
        return TaskResult(success=True, error="".join(output))  # Return the final PRD content
        # result = str(response.content)

        # # second iteration
        # response = chat_model.invoke(
        #     [
        #         {"role": "system", "content": "Yoy are a project manager who create PRD using below instruction/format \n\n"+instruction},
        #         {"role": "user", "content": f"Create a PRD document for {topic}."},
        #         {"role": "assistant", "content": result},
        #         {"role": "user", "content": "Use your asumptions to fill in the gaps and make it more complete."}
        #     ]
        # )

        # logging.info("Successfully created PRD")
        # logging.info("=" * 50)
        # logging.info(f"Loaded PRD instruction template: {result[:100]}...")
        # return TaskResult(success=True, content=result)

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
        # task_result = createTask(prd_result.content).result()
        # if not task_result.success:
        #     return {
        #         "success": False,
        #         "error": task_result.error,
        #         "stage": "Task List Creation"
        #     }
        
        # Success case
        logging.info("Successfully completed project manager workflow")
        return {
            "success": True,
            "prd": prd_result.content,
            # "task_list": task_result.content
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
    ]

    for topic in test_topics:
        print(f"\n{'='*50}\nProcessing topic: {topic}\n{'='*50}")
        result = projectManager.invoke(topic)
        
        if result["success"]:
            print("\nProject Manager Result:")
            print("\nPRD:")
            print(result["prd"])
            # print("\nTask List:")
            # print(result["task_list"])
        else:
            print(f"\nError in {result['stage']}:")
            print(result["error"])

if __name__ == "__main__":
    main()