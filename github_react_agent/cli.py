"""
Command-line interface for GitHub ReAct Agent.
"""

import argparse
import logging
import os
import sys
from typing import List, Optional

from github_react_agent.agent import create_agent
from github_react_agent.config import config, validate_config, ModelProvider

# Disable LangSmith warnings
os.environ["LANGCHAIN_TRACING_V2"] = "false"

def setup_logger(verbose: bool = False) -> None:
    """Set up logging configuration."""
    logging_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="GitHub ReAct Agent - Interact with GitHub using natural language"
    )
    
    # Query arguments
    parser.add_argument(
        "query",
        nargs="?",
        help="The query to send to the agent (if not provided, interactive mode is used)",
    )
    
    # Model configuration
    model_group = parser.add_argument_group("Model Configuration")
    model_group.add_argument(
        "--provider",
        choices=["openai", "vertex", "azure"],
        help="Model provider to use",
    )
    model_group.add_argument(
        "--model",
        help="Specific model to use (e.g., gpt-4, gemini-1.5-pro)",
    )
    model_group.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for the model (0.0 to 1.0)",
    )
    
    # Vertex AI specific options
    vertex_group = parser.add_argument_group("Vertex AI Configuration")
    vertex_group.add_argument(
        "--use-vertex-agent",
        action="store_true",
        help="Use Vertex AI agent implementation (legacy option, ignored)",
    )
    vertex_group.add_argument(
        "--vertex-project",
        help="Google Cloud project ID for Vertex AI",
    )
    vertex_group.add_argument(
        "--vertex-location",
        default="us-central1",
        help="Google Cloud region for Vertex AI",
    )
    
    # Output configuration
    output_group = parser.add_argument_group("Output Configuration")
    output_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    output_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress agent thinking process (overrides --verbose)",
    )
    
    # Version information
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )
    
    return parser.parse_args(args)


def interactive_mode(agent: any) -> None:
    """Run the agent in interactive mode."""
    print("\nGitHub ReAct Agent Interactive Mode")
    print("Type 'exit', 'quit', or Ctrl+D to exit\n")
    
    try:
        while True:
            # Get user input
            try:
                query = input("> ")
            except EOFError:
                print("\nExiting...")
                break
                
            # Check for exit commands
            if query.lower() in ("exit", "quit", "q"):
                print("Exiting...")
                break
                
            if not query.strip():
                continue
                
            # Process the query
            try:
                response = agent.invoke({"input": query})
                output = response.get("output", "No response from agent")
                
                # Print the response
                print("\n" + output + "\n")
                
            except Exception as e:
                print(f"\nError: {str(e)}\n")
    
    except KeyboardInterrupt:
        print("\nExiting...")


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    # Parse arguments
    parsed_args = parse_args(args)
    
    # Show version and exit if requested
    if parsed_args.version:
        from github_react_agent import __version__
        print(f"GitHub ReAct Agent v{__version__}")
        return 0
    
    # Set up logging
    setup_logger(parsed_args.verbose)
    
    # Update configuration from command-line arguments
    if parsed_args.provider:
        config.model_provider = ModelProvider.from_string(parsed_args.provider)
    
    if parsed_args.vertex_project:
        config.vertex_project = parsed_args.vertex_project
    
    if parsed_args.vertex_location:
        config.vertex_location = parsed_args.vertex_location
    
    # Validate configuration
    if not validate_config():
        return 1
    
    # Set verbosity (quiet overrides verbose)
    verbose = parsed_args.verbose and not parsed_args.quiet
    
    try:
        # Create the agent
        agent = create_agent(
            model_name=parsed_args.model,
            temperature=parsed_args.temperature,
            # use_vertex_agent flag is kept for backward compatibility but ignored
            verbose=verbose,
        )
        
        # Run the agent based on mode
        if parsed_args.query:
            # Single query mode
            response = agent.invoke({"input": parsed_args.query})
            print(response.get("output", "No response from agent"))
        else:
            # Interactive mode
            interactive_mode(agent)
            
        return 0
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())