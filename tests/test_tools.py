"""
Tests for GitHub tools.
"""

import pytest
from unittest.mock import patch, MagicMock

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException
from github_react_agent.tools.repo_search import GitHubSearchRepositoriesTool
from github_react_agent.tools.repo_details import GitHubRepoDetailsTool
from github_react_agent.tools.repo_contents import GitHubListContentsTool
from github_react_agent.tools.file_content import GitHubGetFileContentTool


class TestGitHubBaseTool:
    """Tests for the GitHubBaseTool class."""
    
    def test_get_headers(self):
        """Test that headers are correctly generated."""
        tool = GitHubBaseTool(github_token="test_token")
        headers = tool._get_headers()
        
        assert headers["Authorization"] == "token test_token"
        assert headers["Accept"] == "application/vnd.github.v3+json"
    
    @patch("requests.request")
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_request.return_value = mock_response
        
        # Test
        tool = GitHubBaseTool(github_token="test_token")
        result = tool._make_request("GET", "/test")
        
        # Verify
        assert result == {"key": "value"}
        mock_request.assert_called_once()
    
    @patch("requests.request")
    def test_make_request_error(self, mock_request):
        """Test API request that returns an error."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.json.return_value = {"message": "Resource not found"}
        mock_request.return_value = mock_response
        
        # Test
        tool = GitHubBaseTool(github_token="test_token")
        
        # Verify
        with pytest.raises(GitHubToolException):
            tool._make_request("GET", "/test")


class TestGitHubSearchRepositoriesTool:
    """Tests for the GitHubSearchRepositoriesTool class."""
    
    @patch.object(GitHubBaseTool, "_make_request")
    def test_search_repositories_success(self, mock_make_request):
        """Test successful repository search."""
        # Setup mock
        mock_make_request.return_value = {
            "total_count": 2,
            "items": [
                {
                    "full_name": "test/repo1",
                    "description": "Test repo 1",
                    "stargazers_count": 100,
                    "forks_count": 50,
                    "language": "Python",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "html_url": "https://github.com/test/repo1"
                },
                {
                    "full_name": "test/repo2",
                    "description": None,
                    "stargazers_count": 200,
                    "forks_count": 100,
                    "language": None,
                    "updated_at": "2023-01-02T00:00:00Z",
                    "html_url": "https://github.com/test/repo2"
                }
            ]
        }
        
        # Test
        tool = GitHubSearchRepositoriesTool()
        result = tool._run("test")
        
        # Verify
        assert "Found 2 repositories" in result
        assert "test/repo1" in result
        assert "test/repo2" in result
        assert "No description" in result  # Test handling of None values
        mock_make_request.assert_called_once()
    
    @patch.object(GitHubBaseTool, "_make_request")
    def test_search_repositories_no_results(self, mock_make_request):
        """Test repository search with no results."""
        # Setup mock
        mock_make_request.return_value = {"total_count": 0, "items": []}
        
        # Test
        tool = GitHubSearchRepositoriesTool()
        result = tool._run("nonexistent")
        
        # Verify
        assert "No repositories found" in result
        mock_make_request.assert_called_once()
