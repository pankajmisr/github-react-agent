"""
Configuration management for GitHub ReAct Agent.
Handles environment variables and other configuration options.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ModelProvider(str, Enum):
    """Supported model providers."""
    OPENAI = "openai"
    VERTEX = "vertex"
    AZURE = "azure"
    
    @classmethod
    def from_string(cls, value: Optional[str]) -> "ModelProvider":
        """Convert string to ModelProvider enum."""
        if not value:
            return cls.OPENAI
        
        try:
            return cls(value.lower())
        except ValueError:
            print(f"Warning: Unknown model provider '{value}'. Using default (OpenAI).")
            return cls.OPENAI


@dataclass
class Config:
    """Configuration for GitHub ReAct Agent."""
    # GitHub API configuration
    github_api_token: str = ""
    github_api_url: str = "https://api.github.com"
    
    # Model provider configuration
    model_provider: ModelProvider = ModelProvider.OPENAI
    openai_api_key: str = ""
    vertex_project: Optional[str] = None
    vertex_location: str = "us-central1"
    
    # Agent configuration
    verbose: bool = True
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create a Config instance from environment variables."""
        config = cls()
        
        # GitHub configuration
        config.github_api_token = os.getenv("GITHUB_API_TOKEN", "")
        config.github_api_url = os.getenv("GITHUB_API_URL", config.github_api_url)
        
        # Model provider configuration
        provider_str = os.getenv("MODEL_PROVIDER")
        config.model_provider = ModelProvider.from_string(provider_str)
        
        config.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        config.vertex_project = os.getenv("VERTEX_PROJECT")
        config.vertex_location = os.getenv("VERTEX_LOCATION", config.vertex_location)
        
        # Agent configuration
        config.verbose = os.getenv("VERBOSE", "true").lower() in ("true", "1", "yes")
        
        return config


# Default config instance
config = Config.from_env()


def validate_config() -> bool:
    """Validate the configuration."""
    is_valid = True
    
    # Check GitHub API token
    if not config.github_api_token:
        print("Error: GITHUB_API_TOKEN is not set.")
        is_valid = False
    
    # Check model provider-specific configuration
    if config.model_provider == ModelProvider.OPENAI and not config.openai_api_key:
        print("Error: OPENAI_API_KEY is not set.")
        is_valid = False
    
    if config.model_provider == ModelProvider.VERTEX and not config.vertex_project:
        print("Warning: VERTEX_PROJECT is not set. Using default project from credentials.")
    
    return is_valid