"""
Tool for creating commits on GitHub.
"""

import base64
from typing import ClassVar, Dict, List, Optional

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubCommitFileTool(GitHubBaseTool):
    """Tool for committing a file to a GitHub repository."""
    name: ClassVar[str] = "github_commit_file"
    description: ClassVar[str] = """
    Create or update a file in a GitHub repository.
    Input should be a JSON-formatted string with the following fields:
    - repo_full_name: Repository name in the format "owner/repo"
    - path: Path where to create/update the file
    - content: Content of the file
    - message: Commit message
    - branch: Branch to commit to (usually "main" or "master")
    - sha: SHA of the file being replaced (required only when updating existing files)
    
    Example for creating a new file:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "path": "docs/example.md",
        "content": "# Example File\n\nThis is an example file.",
        "message": "Add example documentation file",
        "branch": "main"
    }
    
    Example for updating an existing file:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "path": "docs/example.md",
        "content": "# Updated Example File\n\nThis file has been updated.",
        "message": "Update example documentation file",
        "branch": "main",
        "sha": "abc123def456..."
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: JSON-formatted string with commit details
            
        Returns:
            Response message with commit status
        """
        try:
            import json
            
            # Parse the input
            try:
                commit_data = json.loads(input_str)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format. Please provide valid JSON."
            
            # Validate required fields
            required_fields = ["repo_full_name", "path", "content", "message", "branch"]
            for field in required_fields:
                if field not in commit_data:
                    return f"Error: Missing required field '{field}'."
            
            # Extract repository owner and name
            repo_full_name = commit_data["repo_full_name"]
            if "/" not in repo_full_name:
                return "Error: Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            
            # Prepare request body
            request_body = {
                "message": commit_data["message"],
                "content": base64.b64encode(commit_data["content"].encode("utf-8")).decode("utf-8"),
                "branch": commit_data["branch"],
            }
            
            # Add SHA if provided (for updating existing files)
            if "sha" in commit_data:
                request_body["sha"] = commit_data["sha"]
            
            # Create or update file
            response = self._make_request(
                method="PUT",
                endpoint=f"/repos/{owner}/{repo}/contents/{commit_data['path']}",
                json=request_body
            )
            
            # Format the response
            if "content" in response and response["content"] is not None:
                file_path = response["content"]["path"]
                commit_sha = response["commit"]["sha"]
                file_url = response["content"]["html_url"]
                action = "updated" if "sha" in commit_data else "created"
                
                return f"Successfully {action} file '{file_path}' in commit {commit_sha[:7]}\nFile URL: {file_url}"
            else:
                return f"File operation completed, but full details not available."
            
        except GitHubToolException as e:
            return f"Error committing file: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


class GitHubCommitMultipleFilesTool(GitHubBaseTool):
    """Tool for committing multiple files to a GitHub repository in a single commit."""
    name: ClassVar[str] = "github_commit_multiple_files"
    description: ClassVar[str] = """
    Create or update multiple files in a GitHub repository with a single commit.
    Input should be a JSON-formatted string with the following fields:
    - repo_full_name: Repository name in the format "owner/repo"
    - files: Array of file objects, each containing "path" and "content"
    - message: Commit message
    - branch: Branch to commit to (usually "main" or "master")
    
    Example:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "files": [
            {
                "path": "docs/example1.md",
                "content": "# Example File 1\\n\\nThis is the first example file."
            },
            {
                "path": "docs/example2.md",
                "content": "# Example File 2\\n\\nThis is the second example file."
            }
        ],
        "message": "Add example documentation files",
        "branch": "main"
    }
    """
    
    def _get_current_commit_sha(self, owner: str, repo: str, branch: str) -> str:
        """Get the current commit SHA for a branch."""
        branch_data = self._make_request(
            method="GET",
            endpoint=f"/repos/{owner}/{repo}/branches/{branch}"
        )
        return branch_data["commit"]["sha"]
    
    def _get_tree_sha(self, owner: str, repo: str, commit_sha: str) -> str:
        """Get the tree SHA for a commit."""
        commit_data = self._make_request(
            method="GET",
            endpoint=f"/repos/{owner}/{repo}/git/commits/{commit_sha}"
        )
        return commit_data["tree"]["sha"]
    
    def _create_tree(self, owner: str, repo: str, base_tree_sha: str, files: List[Dict[str, str]]) -> str:
        """Create a new Git tree with the specified files."""
        tree_items = []
        for file in files:
            tree_items.append({
                "path": file["path"],
                "mode": "100644",  # Normal file mode
                "type": "blob",
                "content": file["content"]
            })
        
        tree_data = self._make_request(
            method="POST",
            endpoint=f"/repos/{owner}/{repo}/git/trees",
            json={
                "base_tree": base_tree_sha,
                "tree": tree_items
            }
        )
        return tree_data["sha"]
    
    def _create_commit(self, owner: str, repo: str, message: str, tree_sha: str, parent_commit_sha: str) -> str:
        """Create a new commit using the specified tree."""
        commit_data = self._make_request(
            method="POST",
            endpoint=f"/repos/{owner}/{repo}/git/commits",
            json={
                "message": message,
                "tree": tree_sha,
                "parents": [parent_commit_sha]
            }
        )
        return commit_data["sha"]
    
    def _update_branch_ref(self, owner: str, repo: str, branch: str, commit_sha: str) -> None:
        """Update a branch reference to point to a specific commit."""
        self._make_request(
            method="PATCH",
            endpoint=f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
            json={
                "sha": commit_sha,
                "force": False
            }
        )
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: JSON-formatted string with commit details
            
        Returns:
            Response message with commit status
        """
        try:
            import json
            
            # Parse the input
            try:
                commit_data = json.loads(input_str)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format. Please provide valid JSON."
            
            # Validate required fields
            required_fields = ["repo_full_name", "files", "message", "branch"]
            for field in required_fields:
                if field not in commit_data:
                    return f"Error: Missing required field '{field}'."
            
            # Validate files array
            files = commit_data["files"]
            if not isinstance(files, list) or len(files) == 0:
                return "Error: 'files' must be a non-empty array of file objects."
            
            for file in files:
                if "path" not in file or "content" not in file:
                    return "Error: Each file object must have 'path' and 'content' fields."
            
            # Extract repository owner and name
            repo_full_name = commit_data["repo_full_name"]
            if "/" not in repo_full_name:
                return "Error: Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            branch = commit_data["branch"]
            message = commit_data["message"]
            
            # Perform Git operations to create a commit with multiple files
            try:
                # Get current commit SHA
                current_commit_sha = self._get_current_commit_sha(owner, repo, branch)
                
                # Get tree SHA for the current commit
                base_tree_sha = self._get_tree_sha(owner, repo, current_commit_sha)
                
                # Create a new tree with the files
                new_tree_sha = self._create_tree(owner, repo, base_tree_sha, files)
                
                # Create a new commit using the new tree
                new_commit_sha = self._create_commit(owner, repo, message, new_tree_sha, current_commit_sha)
                
                # Update the branch reference to point to the new commit
                self._update_branch_ref(owner, repo, branch, new_commit_sha)
                
                # Format response
                file_count = len(files)
                file_list = ", ".join(f"'{file['path']}'" for file in files)
                
                return (
                    f"Successfully committed {file_count} files to {owner}/{repo} on branch '{branch}'.\n"
                    f"Commit message: '{message}'\n"
                    f"Commit SHA: {new_commit_sha[:7]}\n"
                    f"Files: {file_list}"
                )
                
            except GitHubToolException as e:
                return f"Error during Git operation: {str(e)}"
            
        except GitHubToolException as e:
            return f"Error committing files: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
