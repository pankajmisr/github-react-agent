"""
Tool for searching GitHub repositories.
"""

from typing import Optional

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubSearchRepositoriesTool(GitHubBaseTool):
    """Tool for searching GitHub repositories."""
    name = "github_search_repositories"
    description = """
    Search for GitHub repositories based on a query.
    Input should be a search query string.
    Examples:
    - "language:python stars:>1000"
    - "react native"
    - "machine learning language:python stars:>500 created:>2022-01-01"
    - "user:microsoft language:typescript"
    - "org:tensorflow"
    
    Useful search qualifiers:
    - language:[language] - Filter by programming language
    - stars:[number] or stars:>[number] - Filter by stars
    - created:[date] - Filter by creation date
    - pushed:[date] - Filter by last update date
    - user:[username] - Repositories from a specific user
    - org:[org] - Repositories from a specific organization
    """
    
    def _run(self, query: str, per_page: Optional[int] = 5) -> str:
        """
        Run the tool with the provided query.
        
        Args:
            query: Search query string
            per_page: Number of results to return (default: 5)
            
        Returns:
            Formatted search results
        """
        try:
            # Set a reasonable default if per_page is None or invalid
            if per_page is None or per_page < 1:
                per_page = 5
            if per_page > 100:
                per_page = 100
                
            results = self._make_request(
                method="GET",
                endpoint="/search/repositories",
                params={"q": query, "per_page": per_page}
            )
            
            if results["total_count"] == 0:
                return "No repositories found matching your query."
            
            repos = results["items"]
            response = f"Found {results['total_count']} repositories matching your query. Here are the top {len(repos)} results:\n\n"
            
            for i, repo in enumerate(repos, 1):
                response += f"{i}. {repo['full_name']}\n"
                response += f"   Description: {repo['description'] or 'No description'}\n"
                response += f"   Language: {repo['language'] or 'Not specified'}\n"
                response += f"   Stars: {repo['stargazers_count']}, Forks: {repo['forks_count']}\n"
                response += f"   Updated: {repo['updated_at']}\n"
                response += f"   URL: {repo['html_url']}\n\n"
            
            return response
        
        except GitHubToolException as e:
            return f"Error searching repositories: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"