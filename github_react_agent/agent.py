"""
GitHub ReAct Agent implementation.

This module contains the implementation of the GitHub ReAct agent,
which can reason about and interact with GitHub repositories.
"""

import logging
from typing import Any, Dict, List, Optional, Sequence, Union

# LangChain imports
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain.prompts import PromptTemplate
from langchain import hub

# OpenAI implementation
from langchain_openai import ChatOpenAI

# For Vertex AI support (optional)
try:
    from vertexai import agent_engines
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

# Internal imports
from github_react_agent.config import config, ModelProvider
from github_react_agent.tools import get_github_tools

# Set up logging
logger = logging.getLogger(__name__)

# Default ReAct prompt - will use the one from hub, but have a fallback
DEFAULT_REACT_PROMPT = PromptTemplate.from_template("""
You are an agent designed to interact with GitHub API.
You have access to the following tools:

{tools}

You must follow this format:

Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

When you have a response for the human, respond with:

Thought: I know the answer
Final Answer: the final answer to the human's question

Begin!

Question: {input}
Thought: """)


def react_builder(
    model: BaseLanguageModel,
    *,
    tools: Sequence[BaseTool],
    prompt: BasePromptTemplate,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> AgentExecutor:
    """
    Build a ReAct agent using the provided model, tools, and prompt.
    
    Args:
        model: Language model to use
        tools: Tools available to the agent
        prompt: Prompt template for the agent
        agent_executor_kwargs: Additional arguments for the AgentExecutor
        
    Returns:
        An AgentExecutor instance
    """
    agent_executor_kwargs = agent_executor_kwargs or {}
    
    # Create the agent
    agent = create_react_agent(model, tools, prompt)
    
    # Create and return the executor
    # Don't add verbose here - it will be in agent_executor_kwargs if needed
    return AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        **agent_executor_kwargs
    )


def get_model(
    model_name: Optional[str] = None,
    provider: Optional[Union[str, ModelProvider]] = None,
    temperature: float = 0.0,
) -> BaseLanguageModel:
    """
    Get a language model based on configuration.
    
    Args:
        model_name: Name of the model to use
        provider: Provider to use (openai, vertex, etc.)
        temperature: Temperature for the model
        
    Returns:
        A language model instance
    """
    # Determine provider
    if provider is None:
        provider = config.model_provider
    elif isinstance(provider, str):
        provider = ModelProvider.from_string(provider)
    
    # Get model based on provider
    if provider == ModelProvider.OPENAI:
        # Default model if not specified
        if model_name is None:
            model_name = "gpt-4o"
            
        return ChatOpenAI(
            temperature=temperature,
            model=model_name,
            streaming=True,
        )
    
    elif provider == ModelProvider.VERTEX and VERTEX_AVAILABLE:
        # Import here to avoid errors if not available
        from langchain_google_vertexai import ChatVertexAI
        
        # Default model if not specified
        if model_name is None:
            model_name = "gemini-1.5-pro"
            
        return ChatVertexAI(
            temperature=temperature,
            model_name=model_name,
            project=config.vertex_project,
            location=config.vertex_location,
        )
    
    elif provider == ModelProvider.AZURE:
        # For Azure OpenAI - requires additional configuration
        from langchain_openai import AzureChatOpenAI
        
        # Default model if not specified
        if model_name is None:
            model_name = "gpt-4"
            
        return AzureChatOpenAI(
            temperature=temperature,
            model=model_name,
            streaming=True,
        )
    
    else:
        # Fallback to OpenAI if provider not supported
        logger.warning(
            f"Provider {provider} not supported or not available. Using OpenAI instead."
        )
        return ChatOpenAI(
            temperature=temperature, 
            model=model_name or "gpt-4o"
        )


def create_agent(
    model: Optional[BaseLanguageModel] = None,
    tools: Optional[List[BaseTool]] = None,
    prompt: Optional[BasePromptTemplate] = None,
    use_vertex_agent: bool = False,
    verbose: Optional[bool] = None,
    **kwargs,
) -> Any:
    """
    Create a GitHub ReAct agent.
    
    Args:
        model: Language model to use
        tools: Tools to make available to the agent
        prompt: Prompt template for the agent
        use_vertex_agent: Whether to use Vertex AI's agent implementation
        verbose: Whether to enable verbose output
        **kwargs: Additional arguments for the agent
        
    Returns:
        An agent that can interact with GitHub
    """
    # Set up tools
    if tools is None:
        tools = get_github_tools()
    
    # Set up model
    if model is None:
        model = get_model()
    
    # Set up prompt
    if prompt is None:
        try:
            # Try to get the prompt from the hub
            prompt = hub.pull("hwchase17/react")
        except Exception as e:
            logger.warning(f"Failed to pull prompt from hub: {e}. Using default prompt.")
            prompt = DEFAULT_REACT_PROMPT
    
    # Set verbosity
    if verbose is not None:
        config.verbose = verbose
    
    # Prepare agent executor kwargs
    agent_executor_kwargs = kwargs.copy()
    agent_executor_kwargs["verbose"] = config.verbose
    
    # Create the agent
    if use_vertex_agent and VERTEX_AVAILABLE:
        # Create a Vertex AI agent
        agent = agent_engines.LangchainAgent(
            model=model,
            tools=tools,
            prompt=prompt,
            agent_executor_kwargs=agent_executor_kwargs,
            runnable_builder=react_builder,
        )
    else:
        # Create a regular LangChain agent
        agent = react_builder(
            model=model,
            tools=tools,
            prompt=prompt,
            agent_executor_kwargs=agent_executor_kwargs
        )
    
    return agent