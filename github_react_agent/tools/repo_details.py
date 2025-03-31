"""
Tool for getting details about a GitHub repository.
"""

from typing import ClassVar

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubRepoDetailsTool(GitHubBaseTool):
    """Tool for getting details about a GitHub repository."""
    name: ClassVar[str] = "github_repo_details"
    description: ClassVar[str] = """
    Get detailed information about a GitHub repository.
    Input should be in the format "owner/repo".
    Examples:
    - "langchain-ai/langchain"
    - "facebook/react"
    - "tensorflow/tensorflow"
    - "microsoft/vscode"
    """
    
    def _run(self, repo_full_name: str) -> str:
        """
        Run the tool with the provided repository name.
        
        Args:
            repo_full_name: Repository name in the format "owner/repo"
            
        Returns:
            Formatted repository details
        """
        try:
            if "/" not in repo_full_name:
                return "Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            
            # Get repository details
            repo_data = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}"
            )
            
            # Get repository languages
            languages_data = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/languages"
            )
            
            # Format languages by percentage
            total_bytes = sum(languages_data.values())
            languages_str = ", ".join(
                f"{lang} ({bytes / total_bytes:.1%})" 
                for lang, bytes in sorted(languages_data.items(), key=lambda x: x[1], reverse=True)
            ) if total_bytes > 0 else "No language data available"
            
            # Build response
            response = f"# {repo_data['full_name']}\n\n"
            
            # Basic info
            response += f"**Description**: {repo_data['description'] or 'No description'}\n\n"
            response += f"**Owner**: {repo_data['owner']['login']} ({repo_data['owner']['type']})\n"
            response += f"**Created**: {repo_data['created_at']}\n"
            response += f"**Last Updated**: {repo_data['updated_at']}\n"
            response += f"**Default Branch**: {repo_data['default_branch']}\n\n"
            
            # Stats
            response += "## Stats\n\n"
            response += f"**Stars**: {repo_data['stargazers_count']}\n"
            response += f"**Watchers**: {repo_data['watchers_count']}\n"
            response += f"**Forks**: {repo_data['forks_count']}\n"
            response += f"**Open Issues**: {repo_data['open_issues_count']}\n"
            response += f"**Size**: {repo_data['size']} KB\n\n"
            
            # Languages
            response += "## Languages\n\n"
            response += f"{languages_str}\n\n"
            
            # URLs
            response += "## URLs\n\n"
            response += f"**Homepage**: {repo_data['homepage'] or 'N/A'}\n"
            response += f"**GitHub URL**: {repo_data['html_url']}\n"
            response += f"**Clone URL**: {repo_data['clone_url']}\n"
            response += f"**SSH URL**: {repo_data['ssh_url']}\n"
            
            # License
            if repo_data.get('license'):
                response += f"\n**License**: {repo_data['license']['name']}\n"
            
            return response
            
        except GitHubToolException as e:
            return f"Error getting repository details: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"