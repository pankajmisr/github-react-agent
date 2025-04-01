"""
Tools for interacting with GitHub repositories.
"""

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException
from github_react_agent.tools.branch import GitHubCreateBranchTool, GitHubListBranchesTool
from github_react_agent.tools.commit import GitHubCommitFileTool, GitHubCommitMultipleFilesTool
from github_react_agent.tools.file_content import GitHubGetFileContentTool
from github_react_agent.tools.file_metadata import GitHubGetFileMetadataTool
from github_react_agent.tools.pull_request import GitHubCreatePullRequestTool
from github_react_agent.tools.pull_request_review import (
    GitHubReviewPullRequestTool,
    GitHubListPullRequestReviewsTool,
    GitHubGetPullRequestTool,
    GitHubMergePullRequestTool
)
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
    "GitHubGetFileMetadataTool",
    "GitHubCreateBranchTool",
    "GitHubListBranchesTool",
    "GitHubCommitFileTool",
    "GitHubCommitMultipleFilesTool",
    "GitHubCreatePullRequestTool",
    "GitHubReviewPullRequestTool",
    "GitHubListPullRequestReviewsTool",
    "GitHubGetPullRequestTool",
    "GitHubMergePullRequestTool",
    "get_github_tools",
]


def get_github_tools():
    """Get all GitHub tools."""
    return [
        GitHubSearchRepositoriesTool(),
        GitHubRepoDetailsTool(),
        GitHubListContentsTool(),
        GitHubGetFileContentTool(),
        GitHubGetFileMetadataTool(),
        GitHubCreateBranchTool(),
        GitHubListBranchesTool(),
        GitHubCommitFileTool(),
        GitHubCommitMultipleFilesTool(),
        GitHubCreatePullRequestTool(),
        GitHubReviewPullRequestTool(),
        GitHubListPullRequestReviewsTool(),
        GitHubGetPullRequestTool(),
        GitHubMergePullRequestTool()
    ]
