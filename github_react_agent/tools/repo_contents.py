"""
Tool for listing contents of a GitHub repository.
"""

from typing import Dict, List, Optional, ClassVar

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubListContentsTool(GitHubBaseTool):
    """Tool for listing contents of a GitHub repository."""
    name: ClassVar[str] = "github_list_contents"
    description: ClassVar[str] = """
    List the contents of a GitHub repository or directory within a repository.
    Input should be in the format "owner/repo/path" where path is optional.
    Examples:
    - "langchain-ai/langchain" (lists root directory)
    - "langchain-ai/langchain/docs" (lists contents of the docs directory)
    - "tensorflow/tensorflow/tensorflow/python" (lists contents of the tensorflow/python directory)
    """
    
    def _format_item(self, item: Dict, indent: int = 0) -> str:
        """Format a content item for display."""
        icon = "📁 " if item["type"] == "dir" else "📄 "
        return f"{' ' * indent}{icon}{item['name']} ({item['type']})"
    
    def _run(self, path_string: str, ref: Optional[str] = None) -> str:
        """
        Run the tool with the provided path.
        
        Args:
            path_string: Path in the format "owner/repo/path"
            ref: Optional git reference (branch, tag, commit)
            
        Returns:
            Formatted directory listing
        """
        try:
            parts = path_string.split("/")
            if len(parts) < 2:
                return "Invalid input. Please provide at least owner/repo."
            
            owner = parts[0]
            repo = parts[1]
            path = "/".join(parts[2:]) if len(parts) > 2 else ""
            
            # Prepare parameters
            params = {}
            if ref:
                params["ref"] = ref
                
            result = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/contents/{path}",
                params=params
            )
            
            if not isinstance(result, list):
                # This is a file, not a directory
                return (
                    f"'{path}' is a file, not a directory. "
                    f"Use github_get_file_content to view its contents."
                )
            
            # It's a directory, format the listing
            full_path = f"{owner}/{repo}/{path}" if path else f"{owner}/{repo}"
            response = f"# Contents of {full_path}\n\n"
            
            # Group items by type (directories first, then files)
            dirs = [item for item in result if item["type"] == "dir"]
            files = [item for item in result if item["type"] == "file"]
            
            # Sort each group alphabetically
            dirs.sort(key=lambda x: x["name"].lower())
            files.sort(key=lambda x: x["name"].lower())
            
            # Format the listing
            if dirs:
                response += "## Directories\n\n"
                for d in dirs:
                    response += f"- 📁 [{d['name']}]({d['html_url']})\n"
                response += "\n"
            
            if files:
                response += "## Files\n\n"
                for f in files:
                    response += f"- 📄 [{f['name']}]({f['html_url']})\n"
            
            # Add navigation help
            response += "\n## Navigation\n\n"
            
            # Parent directory link if not at root
            if path:
                parent_path = "/".join(parts[:-1]) if len(parts) > 3 else f"{owner}/{repo}"
                response += f"- ⬆️ Parent directory: Use `github_list_contents(\"{parent_path}\")`\n"
            
            # Subdirectory navigation examples
            if dirs:
                response += f"- 📁 View subdirectory: Use `github_list_contents(\"{full_path}/{dirs[0]['name']}\")`\n"
            
            # File content example
            if files:
                response += f"- 📄 View file: Use `github_get_file_content(\"{full_path}/{files[0]['name']}\")`\n"
            
            return response
            
        except GitHubToolException as e:
            return f"Error listing repository contents: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"