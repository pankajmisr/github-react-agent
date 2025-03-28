"""
Tool for getting the content of a file from a GitHub repository.
"""

import base64
from typing import Optional

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubGetFileContentTool(GitHubBaseTool):
    """Tool for getting the content of a file from a GitHub repository."""
    name = "github_get_file_content"
    description = """
    Get the content of a file from a GitHub repository.
    Input should be in the format "owner/repo/path_to_file".
    Examples:
    - "langchain-ai/langchain/README.md" 
    - "facebook/react/package.json"
    - "microsoft/vscode/src/vs/editor/editor.main.ts"
    """
    
    def _extract_file_extension(self, path: str) -> str:
        """Extract file extension from path."""
        if "." in path:
            return path.split(".")[-1].lower()
        return ""
    
    def _get_language_for_extension(self, extension: str) -> str:
        """Map file extension to language for code formatting."""
        extension_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "jsx",
            "tsx": "tsx",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "cs": "csharp",
            "go": "go",
            "rb": "ruby",
            "php": "php",
            "rs": "rust",
            "swift": "swift",
            "kt": "kotlin",
            "scala": "scala",
            "html": "html",
            "css": "css",
            "scss": "scss",
            "json": "json",
            "yml": "yaml",
            "yaml": "yaml",
            "md": "markdown",
            "sh": "bash",
            "bash": "bash",
            "sql": "sql",
            "r": "r",
            "dockerfile": "dockerfile",
        }
        return extension_map.get(extension, "")
    
    def _run(self, path_string: str, ref: Optional[str] = None) -> str:
        """
        Run the tool with the provided file path.
        
        Args:
            path_string: Path in the format "owner/repo/path_to_file"
            ref: Optional git reference (branch, tag, commit)
            
        Returns:
            Formatted file content
        """
        try:
            parts = path_string.split("/")
            if len(parts) < 3:
                return "Invalid input. Please provide owner/repo/path_to_file."
            
            owner = parts[0]
            repo = parts[1]
            path = "/".join(parts[2:])
            
            # Prepare parameters
            params = {}
            if ref:
                params["ref"] = ref
                
            result = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/contents/{path}",
                params=params
            )
            
            if isinstance(result, list):
                return f"'{path}' is a directory, not a file. Use github_list_contents to list its contents."
            
            # Get metadata
            file_name = result["name"]
            file_size = result.get("size", 0)
            file_url = result["html_url"]
            
            # Check if binary file or too large
            if result.get("encoding") != "base64" or file_size > 1024 * 1024:  # > 1MB
                return (
                    f"File: {file_name}\n"
                    f"Size: {file_size} bytes\n"
                    f"URL: {file_url}\n\n"
                    f"This file is too large or is a binary file that cannot be displayed."
                )
            
            # Decode content
            content = base64.b64decode(result["content"]).decode("utf-8")
            
            # Determine language for code formatting
            extension = self._extract_file_extension(file_name)
            language = self._get_language_for_extension(extension)
            
            # Build response
            response = f"# File: {file_name}\n\n"
            response += f"**Size**: {file_size} bytes\n"
            response += f"**URL**: {file_url}\n\n"
            
            # Truncate if too long
            original_length = len(content)
            max_length = 5000
            if original_length > max_length:
                content = content[:max_length]
                truncation_message = f"\n\n... [Content truncated, showing {max_length} of {original_length} bytes] ...\n"
                content += truncation_message
            
            # Format content
            if language:
                response += f"```{language}\n{content}\n```"
            else:
                response += f"```\n{content}\n```"
            
            return response
            
        except GitHubToolException as e:
            return f"Error getting file content: {str(e)}"
        except UnicodeDecodeError:
            return f"Error: The file appears to be a binary file and cannot be displayed as text."
        except Exception as e:
            return f"Unexpected error: {str(e)}"