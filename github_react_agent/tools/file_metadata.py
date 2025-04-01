"""
Tool for retrieving metadata about files in a GitHub repository.
"""

from typing import ClassVar, Dict, Optional

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubGetFileMetadataTool(GitHubBaseTool):
    """Tool for getting metadata about a file in a GitHub repository."""
    name: ClassVar[str] = "github_get_file_metadata"
    description: ClassVar[str] = """
    Get metadata about a file in a GitHub repository, including its SHA.
    Input should be in the format "owner/repo/path_to_file" or as a JSON string with additional options.
    
    Simple format example:
    "pankajmisr/vendor-contract-app/src/App.js"
    
    JSON format example with branch specification:
    {
        "repo_full_name": "pankajmisr/vendor-contract-app",
        "path": "src/App.js",
        "branch": "feature/some-branch"
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: Repository path in format "owner/repo/path_to_file"
                      or a JSON with repo_full_name, path, and optional branch
            
        Returns:
            File metadata information
        """
        try:
            import json
            
            # Check if input is JSON format
            try:
                data = json.loads(input_str)
                if isinstance(data, dict) and "repo_full_name" in data and "path" in data:
                    repo_full_name = data["repo_full_name"]
                    file_path = data["path"]
                    ref = data.get("branch")  # Optional branch
                else:
                    return "Error: Invalid JSON format. Must include repo_full_name and path."
            except json.JSONDecodeError:
                # Not JSON, try the simple format
                parts = input_str.split("/")
                if len(parts) < 3:
                    return "Error: Invalid input format. Use 'owner/repo/path_to_file' or JSON format."
                
                repo_full_name = f"{parts[0]}/{parts[1]}"
                file_path = "/".join(parts[2:])
                ref = None
            
            # Extract owner and repo
            owner, repo = repo_full_name.split("/", 1)
            
            # Prepare query parameters
            params = {}
            if ref:
                params["ref"] = ref
            
            # Get file metadata
            try:
                file_info = self._make_request(
                    method="GET",
                    endpoint=f"/repos/{owner}/{repo}/contents/{file_path}",
                    params=params
                )
                
                # If it's a directory, return an error
                if isinstance(file_info, list):
                    return f"Error: '{file_path}' is a directory, not a file."
                
                # Format the response
                response = f"# File Metadata: {file_path}\n\n"
                response += f"**Repository**: {owner}/{repo}\n"
                if ref:
                    response += f"**Branch/Ref**: {ref}\n"
                response += f"**Name**: {file_info['name']}\n"
                response += f"**Path**: {file_info['path']}\n"
                response += f"**SHA**: {file_info['sha']}\n"
                response += f"**Size**: {file_info['size']} bytes\n"
                response += f"**Type**: {file_info['type']}\n"
                response += f"**URL**: {file_info['html_url']}\n"
                
                # Add content type/encoding if available
                if "encoding" in file_info:
                    response += f"**Encoding**: {file_info['encoding']}\n"
                
                return response
                
            except GitHubToolException as e:
                if "404" in str(e):
                    # Check if branch exists but file doesn't
                    try:
                        if ref:
                            self._make_request(
                                method="GET",
                                endpoint=f"/repos/{owner}/{repo}/branches/{ref}"
                            )
                            return f"Error: File '{file_path}' not found in branch '{ref}' of repository {owner}/{repo}."
                    except:
                        pass
                        
                    return f"Error: File '{file_path}' not found in repository {owner}/{repo} or branch '{ref or 'default'}' does not exist."
                else:
                    raise
                    
        except GitHubToolException as e:
            return f"Error retrieving file metadata: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
