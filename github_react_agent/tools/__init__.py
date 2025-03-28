"""
Tools for interacting with GitHub repositories.
"""

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException
from github_react_agent.tools.file_content import GitHubGetFileContentTool
from github_react_agent.tools.repo_contents import GitHubListContentsTool
from github_react_agent.tools.repo_details import GitHubRepoDetailsTool
from github_react_agent.tools.repo_search import GitHubSearchRepositoriesTool

__all__ = [
    "GitHubBaseTool",
    "GitHubToolException",
    "GitHubSearchRepositoriesTool",
    "GitHubRepoDetailsTool",
    "GitHubListContentsTool",
    "GitHubGetFileContentTool",
    "get_github_tools",
]


def get_github_tools():
    """Get all GitHub tools."""
    return [
        GitHubSearchRepositoriesTool(),
        GitHubRepoDetailsTool(),
        GitHubListContentsTool(),
        GitHubGetFileContentTool(),
    ]