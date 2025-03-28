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

- Python 3.8+
- GitHub API token

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/github-react-agent.git
cd github-react-agent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Using pip

```bash
pip install github-react-agent
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

4. If using Google Vertex AI, ensure your credentials are properly set up.

## Usage

### Command Line Interface

```bash
# Start the interactive CLI
github-agent

# Or run directly with a question
github-agent "Find Python repositories with more than 10000 stars"
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