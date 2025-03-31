"""
Tool for creating pull requests on GitHub.
"""

from typing import ClassVar, Dict, Optional

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubCreatePullRequestTool(GitHubBaseTool):
    """Tool for creating a pull request on GitHub."""
    name: ClassVar[str] = "github_create_pull_request"
    description: ClassVar[str] = """
    Create a pull request on a GitHub repository.
    Input should be a JSON-formatted string with the following fields:
    - repo_full_name: Repository name in the format "owner/repo"
    - title: Title of the pull request
    - head: The name of the branch where your changes are implemented
    - base: The name of the branch you want the changes pulled into (usually "main" or "master")
    - body: Description of the pull request (optional)
    
    Example:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "title": "Add new feature",
        "head": "feature-branch",
        "base": "main",
        "body": "This PR adds a new feature that..."
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: JSON-formatted string with PR details
            
        Returns:
            Response message with PR creation status
        """
        try:
            import json
            
            # Parse the input
            try:
                pr_data = json.loads(input_str)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format. Please provide valid JSON."
            
            # Validate required fields
            required_fields = ["repo_full_name", "title", "head", "base"]
            for field in required_fields:
                if field not in pr_data:
                    return f"Error: Missing required field '{field}'."
            
            # Extract repository owner and name
            repo_full_name = pr_data["repo_full_name"]
            if "/" not in repo_full_name:
                return "Error: Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            
            # Prepare request body
            request_body = {
                "title": pr_data["title"],
                "head": pr_data["head"],
                "base": pr_data["base"],
            }
            
            # Add optional fields if provided
            if "body" in pr_data:
                request_body["body"] = pr_data["body"]
            
            # Create pull request
            response = self._make_request(
                method="POST",
                endpoint=f"/repos/{owner}/{repo}/pulls",
                json=request_body
            )
            
            # Format the response
            pr_number = response["number"]
            pr_url = response["html_url"]
            return f"Successfully created pull request #{pr_number}: {pr_url}"
            
        except GitHubToolException as e:
            return f"Error creating pull request: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
