"""
Configuration for pytest.
"""

import os
import pytest
from unittest.mock import patch

# Set test environment variables
os.environ["GITHUB_API_TOKEN"] = "test_token"
os.environ["OPENAI_API_KEY"] = "test_openai_key"


@pytest.fixture(autouse=True)
def mock_env_setup():
    """Automatically mock environment setup for all tests."""
    # Patch config to ensure consistent test environment
    with patch("github_react_agent.config.config") as mock_config:
        mock_config.github_api_token = "test_token"
        mock_config.github_api_url = "https://api.github.com"
        mock_config.verbose = True
        yield mock_config