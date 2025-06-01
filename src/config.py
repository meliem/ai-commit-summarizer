"""Configuration module for the AI Commit Summarizer."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Configuration class for the AI Commit Summarizer."""

    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Default language for messages
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    
    # Default commit message style
    DEFAULT_STYLE: str = os.getenv("DEFAULT_STYLE", "descriptive")
    
    @classmethod
    def has_openai_key(cls) -> bool:
        """Check if the OpenAI API key is configured."""
        return cls.OPENAI_API_KEY is not None and cls.OPENAI_API_KEY.strip() != ""


# Create a .env.example file if it doesn't exist
def create_env_example():
    """Create a .env.example file with the required environment variables."""
    env_example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.example')
    
    if not os.path.exists(env_example_path):
        with open(env_example_path, 'w') as f:
            f.write("""# OpenAI API key for AI-powered commit message generation
OPENAI_API_KEY=your_openai_api_key_here

# OpenAI model to use (default: gpt-4o-mini)
# Other options: gpt-3.5-turbo, gpt-4-turbo, etc.
OPENAI_MODEL=gpt-4o-mini

# Default language for messages (en, fr, es, etc.)
DEFAULT_LANGUAGE=en

# Default commit message style (descriptive, conventional, ai)
DEFAULT_STYLE=descriptive
"""
            )


# Create the example env file when the module is imported
create_env_example()
