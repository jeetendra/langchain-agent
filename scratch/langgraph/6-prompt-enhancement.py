import os
from dotenv import load_dotenv
import logging
import argparse
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableLambda
from llms.openai_gpt_4o import gpt4o_mini
from llms.llama_local import local_llama
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from openai import OpenAI
import requests
from pathlib import Path
from datetime import datetime

# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Image Generation Workflow')
parser.add_argument('--use-local-llm', type=lambda x: x.lower() == 'true', default=True,
                   help='Use local LLM (true/false). Defaults to true if not specified.')
args = parser.parse_args()

# Configuration for LLM usage
useLocalLLM = args.use_local_llm
llm = local_llama if useLocalLLM else gpt4o_mini

# Print current mode
logger.info(f"Running in {'local LLM' if useLocalLLM else 'OpenAI'} mode")

class ImageGenerationState(BaseModel):
    """State for image generation process."""
    prompt: str
    enhanced_prompt: str = ""
    image_path: str = ""
    error: Optional[str] = None
    next_state: str = "enhance"

def setup_environment() -> bool:
    """Setup and validate environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables or .env file")
        return False
    os.environ["OPENAI_API_KEY"] = api_key
    return True

def enhance(state: ImageGenerationState) -> ImageGenerationState:
    """Enhance the prompt using LLM."""
    logger.info("Enhancing prompt...")
    try:
        messages = [
            {"role": "system", "content": "You are an expert prompt engineer. Your task is to enhance the given prompt to create better image generation results. Make it more detailed and specific, but keep the original intent, and return updated promp only."},
            {"role": "user", "content": f"Enhance this image generation prompt: {state.prompt}"}
        ]
        
        result = llm.invoke(messages)
        enhanced = str(result.content) if result.content else state.prompt
        
        logger.info(f"Enhanced prompt: {enhanced[:100]}...")  # Log first 100 chars for brevity
        
        # Show the enhanced prompt to user and get feedback
        print(f"\nOriginal prompt: {state.prompt}")
        print(f"Enhanced prompt: {enhanced}")
        
        choice = input("\nDo you want to:\n1. Use this enhanced prompt\n2. Enhance it further\n3. Use original prompt\nChoice (1-3): ").strip()
        
        if choice == "2":
            # User wants further enhancement, update state and continue enhancing
            return ImageGenerationState(
                prompt=enhanced,  # Use enhanced prompt as new base
                enhanced_prompt="",
                image_path="",
                error=None,
                next_state="enhance"  # Continue with enhancement
            )
        elif choice == "3":
            # User prefers original prompt
            return ImageGenerationState(
                prompt=state.prompt,
                enhanced_prompt=state.prompt,
                image_path="",
                error=None,
                next_state="generate"
            )
        else:
            # Default to using the enhanced prompt (choice 1)
            return ImageGenerationState(
                prompt=state.prompt,
                enhanced_prompt=enhanced,
                image_path="",
                error=None,
                next_state="generate"
            )
            
    except Exception as e:
        error_msg = f"Error enhancing prompt: {str(e)}"
        logger.error(error_msg)
        return ImageGenerationState(
            prompt=state.prompt,
            enhanced_prompt="",
            image_path="",
            error=error_msg,
            next_state="generate"
        )

class ImageGenerator:
    """Handle image generation using DALL-E model."""
    
    def __init__(self):
        """Initialize the image generator."""
        if not useLocalLLM:  # Use OpenAI's DALL-E
            self.client = OpenAI()
            self.use_dalle = True
        else:  # Use local LLM for text-to-image conversion simulation
            self.use_dalle = False

    def _generate_filename(self, output_dir: Path) -> Path:
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        return output_dir / filename

    def _simulate_image_generation(self, prompt: str, file_path: Path) -> str:
        """Simulate image generation using local LLM."""
        try:
            # Use local LLM to generate a description of what the image would look like
            messages = [
                {"role": "system", "content": "You are an image generation AI. Create a detailed description of what the image would look like."},
                {"role": "user", "content": f"Describe an image for: {prompt}"}
            ]
            result = llm.invoke(messages)
            description = str(result.content) if result.content else "Image description not available"
            
            # Write the description to a text file with .txt extension
            text_file_path = file_path.with_suffix('.txt')
            with open(text_file_path, 'w') as f:
                f.write(f"Image Description (Simulation Mode)\n")
                f.write(f"===============================\n")
                f.write(f"Original Prompt: {prompt}\n\n")
                f.write(f"Description of what the image would look like:\n")
                f.write(f"----------------------------------------\n")
                f.write(description)
                f.write("\n\nNote: This is a simulation using local LLM. No actual image was generated.")
            return str(text_file_path)  # Return the text file path
        except Exception as e:
            logger.error(f"Error in image simulation: {e}")
            return ""

    def generate(self, prompt: str, 
                size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
                quality: Literal["standard", "hd"] = "standard") -> Optional[str]:
        """Generate an image from a prompt."""
        try:
            # Create output directory
            output_dir = Path("generated_images")
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = self._generate_filename(output_dir)

            if self.use_dalle:
                # Use DALL-E for actual image generation
                response = self.client.images.generate(
                    prompt=prompt,
                    n=1,
                    size=size,
                    model="dall-e-3",
                    quality=quality
                )

                if not response.data or not response.data[0].url:
                    raise ValueError("No image data received from the API")

                # Download and save the image
                image_url = response.data[0].url
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                with open(file_path, "wb") as file:
                    file.write(response.content)
                return str(file_path)
            else:
                # Use local LLM to simulate image generation
                result = self._simulate_image_generation(prompt, file_path)
                if not result:
                    raise ValueError("Failed to generate image description")
                return result

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

def generate(state: ImageGenerationState) -> ImageGenerationState:
    """Generate an image based on the enhanced prompt."""
    if state.error:
        return ImageGenerationState(
            prompt=state.prompt,
            enhanced_prompt=state.enhanced_prompt,
            image_path="",
            error=state.error,
            next_state="end"
        )
        
    logger.info("Generating image...")
    try:
        prompt_to_use = state.enhanced_prompt or state.prompt
        if not prompt_to_use:
            raise ValueError("No prompt available")

        generator = ImageGenerator()
        image_path = generator.generate(prompt_to_use)
        if not image_path:
            raise ValueError("Failed to generate image")

        logger.info(f"Image generated successfully: {image_path}")
        return ImageGenerationState(
            prompt=state.prompt,
            enhanced_prompt=state.enhanced_prompt,
            image_path=image_path,
            error=None,
            next_state="end"
        )
    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        logger.error(error_msg)
        return ImageGenerationState(
            prompt=state.prompt,
            enhanced_prompt=state.enhanced_prompt,
            image_path="",
            error=error_msg,
            next_state="end"
        )

# Create and configure the graph
graph = StateGraph(ImageGenerationState)
graph.add_node("enhance", RunnableLambda(enhance))
graph.add_node("generate", RunnableLambda(generate))

# Define the workflow with conditional edges
graph.add_edge(START, "enhance")
graph.add_conditional_edges(
    "enhance",
    lambda x: x.next_state,
    {
        "enhance": "enhance",  # Loop back for further enhancement
        "generate": "generate"  # Proceed to generation
    }
)
graph.add_conditional_edges(
    "generate",
    lambda x: x.next_state,
    {
        "end": END
    }
)

# Compile the graph
app = graph.compile()

def main():
    """Main function to run the image generation process."""
    if not setup_environment():
        print("Failed to setup environment. Please check your API key.")
        return

    print("\nImage Generation Workflow")
    print("------------------------")
    print("This program will help you enhance your prompt and generate an image.")
    print("You can iteratively improve the prompt until you're satisfied.")
    print("Type 'quit' or 'exit' to end the program.\n")

    while True:
        prompt = input("Enter your image prompt (or 'quit' to exit): ").strip()
        if prompt.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        if len(prompt.split()) < 3:
            print("Please provide a more detailed prompt (at least 3 words)")
            continue

        try:
            initial_state = ImageGenerationState(
                prompt=prompt,
                enhanced_prompt="",
                image_path="",
                error=None,
                next_state="enhance"
            ).model_dump()  # Convert to dict for LangGraph
            
            final_state = app.invoke(initial_state)

            if final_state.get("error"):
                print(f"\nError: {final_state['error']}")
            elif final_state.get("image_path"):
                used_prompt = final_state.get("enhanced_prompt") or final_state.get("prompt")
                print(f"\nFinal prompt used: {used_prompt}")
                print(f"Image generated successfully at: {final_state['image_path']}")
            else:
                print("\nFailed to generate image. Please try again.")

            # Ask if user wants to continue
            if input("\nWould you like to generate another image? (y/n): ").lower().strip() not in ['y', 'yes']:
                print("Goodbye!")
                break

        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            logger.exception("Unexpected error in main loop")
            if input("Would you like to try again? (y/n): ").lower().strip() not in ['y', 'yes']:
                break

if __name__ == "__main__":
    main()