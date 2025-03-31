"""
Tool for working with branches on GitHub.
"""

from typing import ClassVar, Optional

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubCreateBranchTool(GitHubBaseTool):
    """Tool for creating a branch in a GitHub repository."""
    name: ClassVar[str] = "github_create_branch"
    description: ClassVar[str] = """
    Create a new branch in a GitHub repository.
    Input should be a JSON-formatted string with the following fields:
    - repo_full_name: Repository name in the format "owner/repo"
    - branch_name: Name for the new branch
    - from_branch: Source branch to create from (optional, defaults to the repository's default branch)
    
    Example:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "branch_name": "feature/new-tool",
        "from_branch": "main"
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: JSON-formatted string with branch creation details
            
        Returns:
            Response message with branch creation status
        """
        try:
            import json
            
            # Parse the input
            try:
                branch_data = json.loads(input_str)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format. Please provide valid JSON."
            
            # Validate required fields
            if "repo_full_name" not in branch_data:
                return "Error: Missing required field 'repo_full_name'."
            
            if "branch_name" not in branch_data:
                return "Error: Missing required field 'branch_name'."
            
            # Extract repository owner and name
            repo_full_name = branch_data["repo_full_name"]
            if "/" not in repo_full_name:
                return "Error: Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            new_branch_name = branch_data["branch_name"]
            
            # Get the source branch (default or specified)
            from_branch = branch_data.get("from_branch")
            
            # If no source branch specified, get the default branch
            if not from_branch:
                repo_info = self._make_request(
                    method="GET",
                    endpoint=f"/repos/{owner}/{repo}"
                )
                from_branch = repo_info["default_branch"]
            
            # Get the SHA of the latest commit on the source branch
            branch_info = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/branches/{from_branch}"
            )
            sha = branch_info["commit"]["sha"]
            
            # Create the new branch
            response = self._make_request(
                method="POST",
                endpoint=f"/repos/{owner}/{repo}/git/refs",
                json={
                    "ref": f"refs/heads/{new_branch_name}",
                    "sha": sha
                }
            )
            
            # Format the response
            return (
                f"Successfully created branch '{new_branch_name}' in repository {owner}/{repo}\n"
                f"Created from: {from_branch} ({sha[:7]})\n"
                f"Branch URL: {response['url'].replace('api.github.com/repos', 'github.com').replace('/git/refs/heads', '/tree')}"
            )
            
        except GitHubToolException as e:
            return f"Error creating branch: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


class GitHubListBranchesTool(GitHubBaseTool):
    """Tool for listing branches in a GitHub repository."""
    name: ClassVar[str] = "github_list_branches"
    description: ClassVar[str] = """
    List branches in a GitHub repository.
    Input should be the repository name in the format "owner/repo".
    
    Example: "pankajmisr/github-react-agent"
    """
    
    def _run(self, repo_full_name: str) -> str:
        """
        Run the tool with the provided repository name.
        
        Args:
            repo_full_name: Repository name in the format "owner/repo"
            
        Returns:
            Formatted list of branches
        """
        try:
            # Validate repository name format
            if "/" not in repo_full_name:
                return "Error: Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            
            # Get repository info to determine default branch
            repo_info = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}"
            )
            default_branch = repo_info["default_branch"]
            
            # List branches
            branches = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/branches"
            )
            
            # Format the response
            if not branches:
                return f"No branches found in repository {owner}/{repo}."
            
            response = f"# Branches in {owner}/{repo}\n\n"
            
            # Sort branches (default branch first, then alphabetically)
            def sort_key(branch):
                return (0 if branch["name"] == default_branch else 1, branch["name"].lower())
                
            sorted_branches = sorted(branches, key=sort_key)
            
            for branch in sorted_branches:
                is_default = " (default)" if branch["name"] == default_branch else ""
                last_commit = branch["commit"]["sha"][:7]
                branch_url = f"https://github.com/{owner}/{repo}/tree/{branch['name']}"
                
                response += f"- [{branch['name']}{is_default}]({branch_url}) - Latest commit: {last_commit}\n"
            
            return response
            
        except GitHubToolException as e:
            return f"Error listing branches: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
