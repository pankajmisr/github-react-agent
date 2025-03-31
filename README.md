# GitHub ReAct Agent

A powerful agent that can interact with GitHub repositories using the ReAct (Reasoning + Acting) methodology implemented with LangChain.

## Features

- Search GitHub repositories
- Get repository details and metadata
- List repository contents
- View file contents
- Extensible architecture for adding more GitHub operations
- Support for multiple LLM providers (OpenAI, Vertex AI)

## Requirements

- Python 3.9+ (for Vertex AI support)
- Python 3.8+ (for OpenAI support only)
- GitHub API token

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/pankajmisr/github-react-agent.git
cd github-react-agent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package with desired extras
pip install -e .          # Basic installation
pip install -e ".[dev]"   # With development tools
pip install -e ".[vertex]"  # With Vertex AI support
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your GitHub API token:
   ```
   GITHUB_API_TOKEN=your_github_token_here
   ```

3. If using OpenAI, add your API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. If using Google Vertex AI, set the following:
   ```
   MODEL_PROVIDER=vertex
   VERTEX_PROJECT=your-gcp-project-id
   VERTEX_LOCATION=us-central1  # or your preferred region
   ```
   
   You also need to authenticate with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

## Usage

### Command Line Interface

```bash
# Start the interactive CLI
github-agent

# Or run directly with a question
github-agent "Find Python repositories with more than 10000 stars"

# Specify a different model provider
github-agent "Find Python repositories with more than 10000 stars" --provider vertex --vertex-project=your-project-id
```

### Python API

```python
from github_react_agent import create_agent

# Create the agent
agent = create_agent()

# Ask a question
response = agent.invoke({"input": "Show me details about tensorflow/tensorflow"})
print(response["output"])
```

## Using with Vertex AI

For Vertex AI integration:

1. Install with Vertex AI support:
   ```bash
   pip install -e ".[vertex]"
   ```

2. Make sure you have Python 3.9 or newer

3. Set your Google Cloud credentials:
   ```bash
   gcloud auth application-default login
   ```

4. Run with Vertex AI:
   ```bash
   # Set environment variables
   export MODEL_PROVIDER=vertex
   export VERTEX_PROJECT=your-project-id
   
   # Run the agent
   github-agent "Find popular machine learning repositories"
   
   # Or using command-line arguments
   github-agent "Find popular machine learning repositories" --provider vertex --vertex-project=your-project-id
   ```

## Examples

Here are some example queries you can try:

- "Find Python repositories related to machine learning with more than 5000 stars"
- "Show me details of openai/openai-python"
- "List the contents of the src directory in langchain-ai/langchain"
- "Show me the README file of huggingface/transformers"

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Adding New Tools

You can extend the agent by adding new tools in the `github_react_agent/tools/` directory.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.