"""
Tool for reviewing pull requests on GitHub.
"""

from typing import ClassVar, Dict, List, Optional

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubReviewPullRequestTool(GitHubBaseTool):
    """Tool for reviewing a pull request on GitHub."""
    name: ClassVar[str] = "github_review_pull_request"
    description: ClassVar[str] = """
    Review a pull request on GitHub with approval, comments, or requested changes.
    Input should be a JSON-formatted string with the following fields:
    - repo_full_name: Repository name in the format "owner/repo"
    - pull_number: The pull request number
    - event: Review decision, must be one of: "APPROVE", "REQUEST_CHANGES", "COMMENT"
    - body: The review comment text
    - comments: (Optional) List of specific comments on code, each with:
      - path: File path
      - position: Position in the diff
      - body: Comment text
    
    Example:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "pull_number": 5,
        "event": "APPROVE",
        "body": "This looks good to me. Great work!"
    }
    
    Example with line comments:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "pull_number": 5,
        "event": "REQUEST_CHANGES",
        "body": "Please fix the issues mentioned in the comments.",
        "comments": [
            {
                "path": "src/App.js",
                "position": 4,
                "body": "This variable should be renamed for clarity."
            }
        ]
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: JSON-formatted string with review details
            
        Returns:
            Response message with review status
        """
        try:
            import json
            
            # Parse the input
            try:
                review_data = json.loads(input_str)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format. Please provide valid JSON."
            
            # Validate required fields
            required_fields = ["repo_full_name", "pull_number", "event", "body"]
            for field in required_fields:
                if field not in review_data:
                    return f"Error: Missing required field '{field}'."
            
            # Validate event type
            valid_events = ["APPROVE", "REQUEST_CHANGES", "COMMENT"]
            if review_data["event"] not in valid_events:
                return f"Error: Invalid event type. Must be one of: {', '.join(valid_events)}."
            
            # Extract repository owner and name
            repo_full_name = review_data["repo_full_name"]
            if "/" not in repo_full_name:
                return "Error: Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            pull_number = review_data["pull_number"]
            
            # Prepare request body
            request_body = {
                "event": review_data["event"],
                "body": review_data["body"]
            }
            
            # Add comments if provided
            if "comments" in review_data and review_data["comments"]:
                request_body["comments"] = review_data["comments"]
            
            # Submit the review
            response = self._make_request(
                method="POST",
                endpoint=f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
                json=request_body
            )
            
            # Format the response
            review_id = response.get("id")
            event_type = review_data["event"].lower()
            
            if event_type == "approve":
                message = "approved"
            elif event_type == "request_changes":
                message = "requested changes to"
            else:
                message = "commented on"
            
            return f"Successfully {message} pull request #{pull_number} in {owner}/{repo}.\nReview ID: {review_id}"
            
        except GitHubToolException as e:
            return f"Error reviewing pull request: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


class GitHubListPullRequestReviewsTool(GitHubBaseTool):
    """Tool for listing reviews on a pull request."""
    name: ClassVar[str] = "github_list_pull_request_reviews"
    description: ClassVar[str] = """
    List all reviews on a GitHub pull request.
    Input should be in the format "owner/repo/pull_number" or as a JSON object.
    
    Simple format example: "pankajmisr/github-react-agent/5"
    
    JSON format example:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "pull_number": 5
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: Repository and PR details
            
        Returns:
            List of reviews on the pull request
        """
        try:
            import json
            
            # Check if input is JSON format
            try:
                data = json.loads(input_str)
                if isinstance(data, dict) and "repo_full_name" in data and "pull_number" in data:
                    repo_full_name = data["repo_full_name"]
                    pull_number = data["pull_number"]
                else:
                    return "Error: Invalid JSON format. Must include repo_full_name and pull_number."
            except json.JSONDecodeError:
                # Not JSON, try the simple format
                parts = input_str.split("/")
                if len(parts) < 3:
                    return "Error: Invalid input format. Use 'owner/repo/pull_number' or JSON format."
                
                repo_full_name = f"{parts[0]}/{parts[1]}"
                try:
                    pull_number = int(parts[2])
                except ValueError:
                    return "Error: Pull request number must be an integer."
            
            # Extract repository owner and name
            owner, repo = repo_full_name.split("/", 1)
            
            # Get the reviews
            reviews = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
            )
            
            # Format the response
            if not reviews:
                return f"No reviews found for pull request #{pull_number} in {owner}/{repo}."
            
            response = f"# Reviews for Pull Request #{pull_number} in {owner}/{repo}\n\n"
            
            for review in reviews:
                user = review.get("user", {}).get("login", "Unknown")
                state = review.get("state", "UNKNOWN").upper()
                body = review.get("body", "").strip() or "(No comment)"
                
                # Format the state for readability
                if state == "APPROVED":
                    state_display = "✅ APPROVED"
                elif state == "CHANGES_REQUESTED":
                    state_display = "❌ CHANGES REQUESTED"
                elif state == "COMMENTED":
                    state_display = "💬 COMMENTED"
                else:
                    state_display = f"⚪ {state}"
                
                response += f"## Review by {user} - {state_display}\n\n"
                response += f"{body}\n\n"
                
                # Add line-specific comments if available
                if "comments" in review and review["comments"]:
                    response += "### Line Comments:\n\n"
                    for comment in review["comments"]:
                        file_path = comment.get("path", "Unknown file")
                        position = comment.get("position", "?")
                        comment_body = comment.get("body", "").strip()
                        response += f"- **{file_path}:{position}**: {comment_body}\n"
                
                response += "---\n\n"
            
            return response
            
        except GitHubToolException as e:
            return f"Error listing pull request reviews: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


class GitHubGetPullRequestTool(GitHubBaseTool):
    """Tool for getting details about a pull request."""
    name: ClassVar[str] = "github_get_pull_request"
    description: ClassVar[str] = """
    Get detailed information about a GitHub pull request.
    Input should be in the format "owner/repo/pull_number" or as a JSON object.
    
    Simple format example: "pankajmisr/github-react-agent/5"
    
    JSON format example:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "pull_number": 5
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: Repository and PR details
            
        Returns:
            Detailed information about the pull request
        """
        try:
            import json
            
            # Check if input is JSON format
            try:
                data = json.loads(input_str)
                if isinstance(data, dict) and "repo_full_name" in data and "pull_number" in data:
                    repo_full_name = data["repo_full_name"]
                    pull_number = data["pull_number"]
                else:
                    return "Error: Invalid JSON format. Must include repo_full_name and pull_number."
            except json.JSONDecodeError:
                # Not JSON, try the simple format
                parts = input_str.split("/")
                if len(parts) < 3:
                    return "Error: Invalid input format. Use 'owner/repo/pull_number' or JSON format."
                
                repo_full_name = f"{parts[0]}/{parts[1]}"
                try:
                    pull_number = int(parts[2])
                except ValueError:
                    return "Error: Pull request number must be an integer."
            
            # Extract repository owner and name
            owner, repo = repo_full_name.split("/", 1)
            
            # Get the pull request
            pr = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/pulls/{pull_number}"
            )
            
            # Get the pull request files
            files = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/pulls/{pull_number}/files"
            )
            
            # Format the response
            response = f"# Pull Request #{pull_number}: {pr['title']}\n\n"
            
            # Basic info
            response += f"**Status**: {pr['state'].upper()}"
            if pr['merged']:
                response += " (MERGED)"
            response += "\n"
            
            response += f"**Author**: {pr['user']['login']}\n"
            response += f"**Created**: {pr['created_at']}\n"
            if pr['updated_at']:
                response += f"**Updated**: {pr['updated_at']}\n"
            if pr['closed_at']:
                response += f"**Closed**: {pr['closed_at']}\n"
            if pr['merged_at']:
                response += f"**Merged**: {pr['merged_at']}\n"
            
            response += f"**URL**: {pr['html_url']}\n\n"
            
            # Branch info
            response += f"**Base Branch**: {pr['base']['ref']}\n"
            response += f"**Head Branch**: {pr['head']['ref']}\n\n"
            
            # Description
            if pr['body']:
                response += "## Description\n\n"
                response += f"{pr['body']}\n\n"
            
            # Files changed
            if files:
                response += "## Files Changed\n\n"
                for file in files:
                    status = file['status']
                    icon = "➕" if status == "added" else "✏️" if status == "modified" else "🗑️" if status == "removed" else "🔄"
                    changes = f"+{file['additions']}/-{file['deletions']}"
                    response += f"- {icon} **{file['filename']}** ({status}, {changes})\n"
            
            return response
            
        except GitHubToolException as e:
            return f"Error getting pull request details: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


class GitHubMergePullRequestTool(GitHubBaseTool):
    """Tool for merging a pull request."""
    name: ClassVar[str] = "github_merge_pull_request"
    description: ClassVar[str] = """
    Merge a GitHub pull request.
    Input should be a JSON-formatted string with the following fields:
    - repo_full_name: Repository name in the format "owner/repo"
    - pull_number: The pull request number
    - merge_method: (Optional) Merge method to use, one of: "merge" (default), "squash", "rebase"
    - commit_title: (Optional) Title for the automatic commit message
    - commit_message: (Optional) Extra detail to append to automatic commit message
    
    Example:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "pull_number": 5,
        "merge_method": "squash",
        "commit_title": "Implement new feature"
    }
    """
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: JSON-formatted string with merge details
            
        Returns:
            Response message with merge status
        """
        try:
            import json
            
            # Parse the input
            try:
                merge_data = json.loads(input_str)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format. Please provide valid JSON."
            
            # Validate required fields
            required_fields = ["repo_full_name", "pull_number"]
            for field in required_fields:
                if field not in merge_data:
                    return f"Error: Missing required field '{field}'."
            
            # Extract repository owner and name
            repo_full_name = merge_data["repo_full_name"]
            if "/" not in repo_full_name:
                return "Error: Invalid repository name. Please provide in the format 'owner/repo'."
            
            owner, repo = repo_full_name.split("/", 1)
            pull_number = merge_data["pull_number"]
            
            # Prepare request body
            request_body = {}
            
            # Add optional fields if provided
            if "merge_method" in merge_data:
                valid_methods = ["merge", "squash", "rebase"]
                if merge_data["merge_method"] not in valid_methods:
                    return f"Error: Invalid merge method. Must be one of: {', '.join(valid_methods)}."
                request_body["merge_method"] = merge_data["merge_method"]
            
            if "commit_title" in merge_data:
                request_body["commit_title"] = merge_data["commit_title"]
            
            if "commit_message" in merge_data:
                request_body["commit_message"] = merge_data["commit_message"]
            
            # Merge the pull request
            response = self._make_request(
                method="PUT",
                endpoint=f"/repos/{owner}/{repo}/pulls/{pull_number}/merge",
                json=request_body
            )
            
            # Format the response
            if response.get("merged") is True:
                merge_method = merge_data.get("merge_method", "merge")
                return (
                    f"Successfully merged pull request #{pull_number} in {owner}/{repo} using {merge_method} method.\n"
                    f"Commit SHA: {response.get('sha')}\n"
                    f"Message: {response.get('message')}"
                )
            else:
                return f"Failed to merge pull request #{pull_number} in {owner}/{repo}."
            
        except GitHubToolException as e:
            error_message = str(e)
            
            # Handle specific error cases with more helpful messages
            if "Pull Request is not mergeable" in error_message:
                return f"Error: Pull request #{pull_number} in {owner}/{repo} cannot be merged. It may have conflicts that need to be resolved."
            elif "Required status check" in error_message:
                return f"Error: Cannot merge pull request #{pull_number} because required status checks have not passed."
            elif "Pull Request review" in error_message:
                return f"Error: Cannot merge pull request #{pull_number} because it requires reviews."
            else:
                return f"Error merging pull request: {error_message}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
