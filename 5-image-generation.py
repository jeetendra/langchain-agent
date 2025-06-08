from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from typing import Optional, Literal, Dict, Any
import logging
from datetime import datetime
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ImageConfig:
    """Configuration for image generation."""
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024"
    model: Literal["dall-e-2", "dall-e-3"] = "dall-e-3"
    quality: Literal["standard", "hd"] = "standard"
    output_dir: str = "generated_images"
    n: int = 1

class ImageGenerator:
    """Handle image generation using OpenAI's DALL-E model."""
    
    def __init__(self, config: Optional[ImageConfig] = None):
        """Initialize the image generator with configuration."""
        self.config = config or ImageConfig()
        self.client = OpenAI()
        self._setup_output_directory()

    def _setup_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self) -> Path:
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        return Path(self.config.output_dir) / filename

    def _download_image(self, url: str) -> bytes:
        """Download image from URL."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content

    def generate(self, prompt: str) -> Optional[str]:
        """Generate an image from a prompt."""
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            response = self.client.images.generate(
                prompt=prompt,
                n=self.config.n,
                size=self.config.size,
                model=self.config.model,
                quality=self.config.quality
            )

            if not response.data or not response.data[0].url:
                logger.error("No image data received from the API")
                return None

            image_url = response.data[0].url
            logger.info(f"Image generated successfully, downloading from: {image_url}")
            
            image_data = self._download_image(image_url)
            file_path = self._generate_filename()
            
            with open(file_path, "wb") as file:
                file.write(image_data)
                
            logger.info(f"Image saved successfully to: {file_path}")
            return str(file_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading image: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None

class UserInterface:
    """Handle user interaction for image generation."""

    @staticmethod
    def get_prompt() -> Optional[str]:
        """Get and validate the image generation prompt from user input."""
        while True:
            prompt = input("\nEnter your image generation prompt (minimum 3 words, or 'quit' to exit): ").strip()
            
            if prompt.lower() in ['quit', 'exit']:
                return None
                
            if not prompt:
                print("Prompt cannot be empty. Please try again.")
                continue
                
            words = prompt.split()
            if len(words) < 3:
                print("Please provide a more detailed prompt (at least 3 words)")
                continue
                
            return prompt

    @staticmethod
    def get_image_config() -> ImageConfig:
        """Get image configuration from user input."""
        print("\nImage Configuration:")
        print("1. Standard (1024x1024, standard quality)")
        print("2. High Resolution (1792x1024, HD quality)")
        print("3. Portrait (1024x1792, HD quality)")
        
        while True:
            choice = input("Choose configuration (1-3) [default: 1]: ").strip()
            if not choice:
                return ImageConfig()
                
            try:
                choice_num = int(choice)
                if choice_num == 1:
                    return ImageConfig()
                elif choice_num == 2:
                    return ImageConfig(size="1792x1024", quality="hd")
                elif choice_num == 3:
                    return ImageConfig(size="1024x1792", quality="hd")
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    @staticmethod
    def should_continue() -> bool:
        """Ask if user wants to generate another image."""
        response = input("\nWould you like to generate another image? (y/n): ").lower().strip()
        return response in ['y', 'yes']

def setup_environment() -> bool:
    """Setup environment variables and validate configuration."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables or .env file")
        return False
    os.environ["OPENAI_API_KEY"] = api_key
    return True

def main():
    """Main function to run the image generation."""
    if not setup_environment():
        return

    print("Welcome to the Image Generator!")
    print("You can type 'quit' or 'exit' at any time to end the program")
    
    ui = UserInterface()
    
    while True:
        try:
            # Get configuration for this generation
            config = ui.get_image_config()
            generator = ImageGenerator(config)
            
            # Get prompt from user
            prompt = ui.get_prompt()
            if prompt is None:
                print("Goodbye!")
                break
            
            # Generate the image
            output_path = generator.generate(prompt)
            
            if output_path:
                print(f"\nImage generated and saved successfully to: {output_path}")
            else:
                print("\nFailed to generate image. Check the logs for details.")

            if not ui.should_continue():
                print("Goodbye!")
                break

        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if not ui.should_continue():
                break

if __name__ == "__main__":
    main()
