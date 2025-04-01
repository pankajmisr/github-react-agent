"""
Tool for analyzing GitHub pull requests without submitting formal reviews.
"""

import base64
import re
from typing import ClassVar, Dict, List, Optional, Tuple, Any

from github_react_agent.tools.base import GitHubBaseTool, GitHubToolException


class GitHubAnalyzePullRequestTool(GitHubBaseTool):
    """Tool for analyzing a pull request without submitting a formal review."""
    name: ClassVar[str] = "github_analyze_pull_request"
    description: ClassVar[str] = """
    Analyze a pull request and provide insights without submitting a formal review.
    Examines changed files, code quality, potential issues, and offers suggestions.
    Input should be in the format "owner/repo/pull_number" or as a JSON object.
    
    Simple format example: "pankajmisr/github-react-agent/5"
    
    JSON format example with options:
    {
        "repo_full_name": "pankajmisr/github-react-agent",
        "pull_number": 5,
        "analyze_depth": "detailed"  // or "basic" (default)
    }
    """
    
    def _get_file_content(self, owner: str, repo: str, path: str, ref: str) -> str:
        """Get the content of a file from a specific ref."""
        try:
            file_data = self._make_request(
                method="GET",
                endpoint=f"/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref}
            )
            
            if "content" in file_data and file_data["encoding"] == "base64":
                return base64.b64decode(file_data["content"]).decode("utf-8")
            return ""
        except Exception:
            return ""
    
    def _calculate_file_complexity(self, content: str, filename: str) -> Dict[str, Any]:
        """Calculate various complexity metrics for a file."""
        # Extract file extension
        extension = filename.split(".")[-1].lower() if "." in filename else ""
        
        # Initialize metrics
        metrics = {
            "lines": 0,
            "non_empty_lines": 0,
            "max_line_length": 0,
            "avg_line_length": 0,
            "complexity_score": 0,
            "language": self._detect_language(extension),
            "comments": 0,
            "code_lines": 0,
        }
        
        if not content:
            return metrics
        
        # Calculate basic metrics
        lines = content.split("\n")
        metrics["lines"] = len(lines)
        metrics["non_empty_lines"] = sum(1 for line in lines if line.strip())
        
        if metrics["non_empty_lines"] > 0:
            line_lengths = [len(line) for line in lines if line.strip()]
            metrics["max_line_length"] = max(line_lengths) if line_lengths else 0
            metrics["avg_line_length"] = sum(line_lengths) / len(line_lengths) if line_lengths else 0
        
        # Language-specific analysis
        if extension in ["js", "jsx", "ts", "tsx"]:
            # Count comments in JavaScript/TypeScript
            metrics["comments"] = len(re.findall(r"\/\/.*?$|\/\*[\s\S]*?\*\/", content, re.MULTILINE))
            metrics["code_lines"] = metrics["non_empty_lines"] - metrics["comments"]
            
            # Check for complex patterns
            complexity_indicators = [
                len(re.findall(r"function\s+\w+\s*\(", content)),  # Function declarations
                len(re.findall(r"=>\s*[{(]", content)),  # Arrow functions
                len(re.findall(r"if\s*\(", content)),     # If statements
                len(re.findall(r"for\s*\(", content)),    # For loops
                len(re.findall(r"while\s*\(", content)),  # While loops
                len(re.findall(r"switch\s*\(", content)), # Switch statements
                len(re.findall(r"try\s*{", content)),     # Try blocks
                len(re.findall(r"}\s*catch", content)),   # Catch blocks
            ]
            metrics["complexity_score"] = sum(complexity_indicators)
            
        elif extension in ["py"]:
            # Count comments in Python
            metrics["comments"] = len(re.findall(r"#.*?$|\"\"\"[\s\S]*?\"\"\"", content, re.MULTILINE))
            metrics["code_lines"] = metrics["non_empty_lines"] - metrics["comments"]
            
            # Check for complex patterns
            complexity_indicators = [
                len(re.findall(r"def\s+\w+\s*\(", content)),  # Function declarations
                len(re.findall(r"class\s+\w+", content)),     # Class declarations
                len(re.findall(r"if\s+", content)),           # If statements
                len(re.findall(r"for\s+", content)),          # For loops
                len(re.findall(r"while\s+", content)),        # While loops
                len(re.findall(r"try:", content)),            # Try blocks
                len(re.findall(r"except", content)),          # Except blocks
                len(re.findall(r"with\s+", content)),         # With statements
                len(re.findall(r"lambda", content)),          # Lambda expressions
            ]
            metrics["complexity_score"] = sum(complexity_indicators)
            
        elif extension in ["java", "kt", "scala"]:
            # Count comments in Java/Kotlin/Scala
            metrics["comments"] = len(re.findall(r"\/\/.*?$|\/\*[\s\S]*?\*\/", content, re.MULTILINE))
            metrics["code_lines"] = metrics["non_empty_lines"] - metrics["comments"]
            
            # Check for complex patterns
            complexity_indicators = [
                len(re.findall(r"(public|private|protected)\s+\w+\s+\w+\s*\(", content)),  # Method declarations
                len(re.findall(r"class\s+\w+", content)),    # Class declarations
                len(re.findall(r"if\s*\(", content)),        # If statements
                len(re.findall(r"for\s*\(", content)),       # For loops
                len(re.findall(r"while\s*\(", content)),     # While loops
                len(re.findall(r"switch\s*\(", content)),    # Switch statements
                len(re.findall(r"try\s*{", content)),        # Try blocks
                len(re.findall(r"}\s*catch", content)),      # Catch blocks
                len(re.findall(r"@\w+", content)),           # Annotations
            ]
            metrics["complexity_score"] = sum(complexity_indicators)
            
        return metrics
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            "js": "JavaScript",
            "jsx": "JavaScript (React)",
            "ts": "TypeScript",
            "tsx": "TypeScript (React)",
            "py": "Python",
            "java": "Java",
            "kt": "Kotlin",
            "swift": "Swift",
            "go": "Go",
            "rb": "Ruby",
            "php": "PHP",
            "cs": "C#",
            "c": "C",
            "cpp": "C++",
            "h": "C/C++ Header",
            "html": "HTML",
            "css": "CSS",
            "scss": "SCSS",
            "sass": "Sass",
            "less": "Less",
            "md": "Markdown",
            "json": "JSON",
            "yml": "YAML",
            "yaml": "YAML",
            "xml": "XML",
            "sql": "SQL",
            "sh": "Shell",
            "bat": "Batch",
            "ps1": "PowerShell",
            "dockerfile": "Dockerfile",
            "rs": "Rust",
        }
        return language_map.get(extension.lower(), "Unknown")
    
    def _analyze_diff(self, diff: str) -> Dict[str, Any]:
        """Analyze a diff content to identify patterns and quality indicators."""
        analysis = {
            "added_lines": 0,
            "removed_lines": 0,
            "potential_issues": [],
            "observations": [],
        }
        
        if not diff:
            return analysis
        
        lines = diff.split("\n")
        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                analysis["added_lines"] += 1
                
                # Check for potential issues in added code
                if "TODO" in line or "FIXME" in line:
                    analysis["potential_issues"].append(f"Contains TODO or FIXME comment: {line}")
                
                if "console.log" in line:
                    analysis["potential_issues"].append(f"Contains console.log statement: {line}")
                
                if "printStackTrace" in line:
                    analysis["potential_issues"].append(f"Contains printStackTrace call: {line}")
                
                if "debugger" in line:
                    analysis["potential_issues"].append(f"Contains debugger statement: {line}")
                
                # Look for secrets or credentials
                if re.search(r"(password|secret|key|token|auth).*=.*['\"]((?!\{).)*['\"]", line, re.IGNORECASE):
                    analysis["potential_issues"].append(f"May contain hardcoded credential: {line}")
            
            elif line.startswith("-") and not line.startswith("---"):
                analysis["removed_lines"] += 1
        
        # General observations
        if analysis["added_lines"] > 100 and analysis["added_lines"] > analysis["removed_lines"] * 3:
            analysis["observations"].append(f"Large addition of code ({analysis['added_lines']} lines added vs {analysis['removed_lines']} removed)")
        
        if analysis["removed_lines"] > 100 and analysis["removed_lines"] > analysis["added_lines"] * 3:
            analysis["observations"].append(f"Large removal of code ({analysis['removed_lines']} lines removed vs {analysis['added_lines']} added)")
        
        return analysis
    
    def _provide_suggestions(self, file_analysis: Dict[str, Any], diff_analysis: Dict[str, Any], filename: str) -> List[str]:
        """Provide suggestions based on file and diff analysis."""
        suggestions = []
        
        # Complexity-based suggestions
        if file_analysis.get("complexity_score", 0) > 20:
            suggestions.append(f"Consider refactoring {filename} to reduce complexity")
        
        if file_analysis.get("max_line_length", 0) > 100:
            suggestions.append(f"Some lines in {filename} exceed 100 characters, consider breaking them down")
        
        # Diff-based suggestions
        if diff_analysis["potential_issues"]:
            for issue in diff_analysis["potential_issues"]:
                suggestions.append(f"Address potential issue: {issue}")
        
        # Language-specific suggestions
        language = file_analysis.get("language", "")
        if language in ["JavaScript", "JavaScript (React)", "TypeScript", "TypeScript (React)"]:
            if file_analysis.get("code_lines", 0) > 300:
                suggestions.append(f"Consider splitting {filename} into smaller components")
        
        elif language == "Python":
            if file_analysis.get("code_lines", 0) > 500:
                suggestions.append(f"Consider splitting {filename} into smaller modules")
        
        # General suggestions
        if not suggestions and (file_analysis.get("code_lines", 0) > 0 or diff_analysis["added_lines"] > 0):
            suggestions.append(f"No significant issues found in {filename}")
        
        return suggestions
    
    def _run(self, input_str: str) -> str:
        """
        Run the tool with the provided input.
        
        Args:
            input_str: Repository and PR details
            
        Returns:
            Analysis of the pull request
        """
        try:
            import json
            
            # Parse input
            analyze_depth = "basic"  # Default depth
            
            # Check if input is JSON format
            try:
                data = json.loads(input_str)
                if isinstance(data, dict) and "repo_full_name" in data and "pull_number" in data:
                    repo_full_name = data["repo_full_name"]
                    pull_number = data["pull_number"]
                    
                    if "analyze_depth" in data:
                        analyze_depth = data["analyze_depth"]
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
            
            # Format the initial response
            response = f"# Analysis of Pull Request #{pull_number}: {pr['title']}\n\n"
            
            # Add basic info
            response += f"**Author**: {pr['user']['login']}\n"
            response += f"**Base Branch**: {pr['base']['ref']}\n"
            response += f"**Head Branch**: {pr['head']['ref']}\n"
            response += f"**Changed Files**: {len(files)}\n\n"
            
            # Add PR description
            if pr['body']:
                response += "## PR Description\n\n"
                response += f"{pr['body']}\n\n"
            
            # Analyze files
            response += "## File Analysis\n\n"
            
            has_code_changes = False
            file_metrics = []
            analysis_by_file = {}
            total_additions = 0
            total_deletions = 0
            
            for file in files:
                filename = file['filename']
                status = file['status']
                additions = file['additions']
                deletions = file['deletions']
                total_additions += additions
                total_deletions += deletions
                
                # Get the diff content
                diff_content = file.get('patch', '')
                
                # Skip binary files or files without content
                if not diff_content and status != 'removed':
                    response += f"- **{filename}**: {status} (binary file or too large to display)\n"
                    continue
                
                # Get file content from the head branch for detailed analysis
                file_content = ""
                if status != 'removed' and analyze_depth == "detailed":
                    file_content = self._get_file_content(
                        owner=owner,
                        repo=repo,
                        path=filename,
                        ref=pr['head']['ref']
                    )
                
                # Calculate metrics based on file type
                file_analysis = self._calculate_file_complexity(file_content, filename)
                file_analysis["additions"] = additions
                file_analysis["deletions"] = deletions
                file_analysis["status"] = status
                
                # Analyze diff content
                diff_analysis = self._analyze_diff(diff_content)
                
                # Store analysis for summary
                analysis_by_file[filename] = {
                    "file_analysis": file_analysis,
                    "diff_analysis": diff_analysis
                }
                
                # Add file metrics to the collection
                file_metrics.append({
                    "filename": filename,
                    "status": status,
                    "additions": additions,
                    "deletions": deletions,
                    "language": file_analysis["language"],
                    "complexity": file_analysis.get("complexity_score", 0)
                })
                
                # Flag if we have code changes
                if file_analysis["language"] != "Unknown":
                    has_code_changes = True
                
                # Basic info for each file
                status_icon = "➕" if status == "added" else "✏️" if status == "modified" else "🗑️" if status == "removed" else "🔄"
                lang_info = f"({file_analysis['language']})" if file_analysis["language"] != "Unknown" else ""
                response += f"- {status_icon} **{filename}** {lang_info}: {status}, +{additions}/-{deletions} lines\n"
                
                # Add potential issues for the file
                if diff_analysis["potential_issues"]:
                    response += "  - **Potential issues:**\n"
                    for issue in diff_analysis["potential_issues"][:3]:  # Limit to 3 issues per file
                        response += f"    - {issue}\n"
                
                if analyze_depth == "detailed" and file_analysis["complexity_score"] > 10:
                    response += f"  - **Complexity score:** {file_analysis['complexity_score']} (relatively high)\n"
            
            response += "\n"
            
            # Summary section
            response += "## Summary of Changes\n\n"
            response += f"Total lines added: {total_additions}\n"
            response += f"Total lines deleted: {total_deletions}\n"
            response += f"Net change: {total_additions - total_deletions} lines\n\n"
            
            # Analyze complexity if we have code changes
            if has_code_changes:
                # Sort files by complexity
                sorted_by_complexity = sorted(
                    [m for m in file_metrics if m["complexity"] > 0],
                    key=lambda x: x["complexity"],
                    reverse=True
                )
                
                if sorted_by_complexity:
                    response += "### Most Complex Files:\n\n"
                    for file_metric in sorted_by_complexity[:3]:  # Top 3 most complex files
                        response += f"- **{file_metric['filename']}** - Complexity: {file_metric['complexity']}\n"
                    response += "\n"
            
            # Overall quality assessment
            response += "## Quality Assessment\n\n"
            
            # Calculate average complexity score
            if file_metrics:
                avg_complexity = sum(m["complexity"] for m in file_metrics) / len(file_metrics)
                
                if avg_complexity < 5:
                    quality = "The changes appear to be of high quality with low complexity."
                elif avg_complexity < 15:
                    quality = "The changes have moderate complexity, but generally good quality."
                else:
                    quality = "The changes have high complexity and may benefit from refactoring."
                
                response += f"{quality}\n\n"
            
            # Collect suggestions
            all_suggestions = []
            for filename, analysis in analysis_by_file.items():
                file_suggestions = self._provide_suggestions(
                    analysis["file_analysis"], 
                    analysis["diff_analysis"],
                    filename
                )
                all_suggestions.extend(file_suggestions)
            
            if all_suggestions:
                response += "## Suggestions\n\n"
                for suggestion in all_suggestions:
                    response += f"- {suggestion}\n"
            
            # Final review note
            response += "\n## Review Note\n\n"
            response += "This is an automated analysis of the pull request. "
            response += "It identifies potential issues and provides suggestions based on code metrics. "
            response += "However, a human review is still necessary to evaluate the business logic, "
            response += "functional requirements, and context-specific aspects of the changes."
            
            return response
            
        except GitHubToolException as e:
            return f"Error analyzing pull request: {str(e)}"
        except Exception as e:
            return f"Unexpected error during analysis: {str(e)}"
