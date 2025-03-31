"""
Base classes for GitHub tools.
"""

from typing import Dict, Any, Optional, ClassVar, Annotated

import requests
from langchain_core.tools import BaseTool, ToolException
from pydantic import Field

from github_react_agent.config import config


class GitHubToolException(ToolException):
    """Exception raised when a GitHub API call fails."""
    pass


class GitHubBaseTool(BaseTool):
    """Base class for GitHub tools."""
    # The name and description must be class variables with ClassVar annotation
    name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    
    # Pydantic fields that can be instance attributes
    github_token: str = Field(default_factory=lambda: config.github_api_token)
    github_api_url: str = Field(default_factory=lambda: config.github_api_url)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the GitHub API.
        
        Args:
            method: HTTP method to use (GET, POST, etc.)
            endpoint: API endpoint to call (e.g., "/repos/{owner}/{repo}")
            params: Query parameters to include in the request
            json: JSON body to include in the request
            
        Returns:
            Response data as a dictionary
            
        Raises:
            GitHubToolException: If the API request fails
        """
        url = f"{self.github_api_url}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self._get_headers(),
            params=params,
            json=json,
        )
        
        if response.status_code >= 400:
            error_message = f"GitHub API request failed: {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_message += f" - {error_data['message']}"
            except:
                error_message += f" - {response.text}"
                
            raise GitHubToolException(error_message)
        
        return response.json()