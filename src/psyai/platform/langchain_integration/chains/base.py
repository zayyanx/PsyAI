"""
Base chain templates and builders.

This module provides reusable chain templates for common LangChain patterns.
"""

from typing import Any, Dict, List, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough

from psyai.core.logging import get_logger
from psyai.platform.langchain_integration.client import get_langchain_client

logger = get_logger(__name__)


def create_simple_chain(
    template: str,
    input_variables: Optional[List[str]] = None,
    model_name: Optional[str] = None,
) -> Runnable:
    """
    Create a simple LLM chain with a prompt template.

    Args:
        template: Prompt template string
        input_variables: List of input variable names (auto-detected if not provided)
        model_name: Optional model name override

    Returns:
        Runnable chain

    Example:
        >>> chain = create_simple_chain("What is {topic}?")
        >>> response = await chain.ainvoke({"topic": "PsyAI"})
    """
    client = get_langchain_client(model_name=model_name)

    prompt = PromptTemplate(
        template=template,
        input_variables=input_variables or [],
    )

    chain = prompt | client.llm | StrOutputParser()

    logger.debug("simple_chain_created", template_length=len(template))

    return chain


def create_chat_chain(
    system_message: str,
    human_message_template: str,
    model_name: Optional[str] = None,
) -> Runnable:
    """
    Create a chat chain with system and human messages.

    Args:
        system_message: System message (context/instructions)
        human_message_template: Human message template
        model_name: Optional model name override

    Returns:
        Runnable chain

    Example:
        >>> chain = create_chat_chain(
        ...     system_message="You are a helpful AI assistant.",
        ...     human_message_template="Answer this question: {question}"
        ... )
        >>> response = await chain.ainvoke({"question": "What is 2+2?"})
    """
    client = get_langchain_client(model_name=model_name)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", human_message_template),
        ]
    )

    chain = prompt | client.llm | StrOutputParser()

    logger.debug("chat_chain_created")

    return chain


def create_sequential_chain(
    chains: List[Runnable],
    chain_names: Optional[List[str]] = None,
) -> Runnable:
    """
    Create a sequential chain that runs multiple chains in sequence.

    Args:
        chains: List of chains to run sequentially
        chain_names: Optional names for each chain

    Returns:
        Sequential chain

    Example:
        >>> chain1 = create_simple_chain("Summarize: {text}")
        >>> chain2 = create_simple_chain("Translate to Spanish: {text}")
        >>> sequential = create_sequential_chain([chain1, chain2])
    """
    if not chains:
        raise ValueError("At least one chain is required")

    # Chain them together with pipe operator
    result = chains[0]
    for chain in chains[1:]:
        result = result | chain

    logger.debug("sequential_chain_created", chain_count=len(chains))

    return result


def create_map_reduce_chain(
    map_template: str,
    reduce_template: str,
    model_name: Optional[str] = None,
) -> Dict[str, Runnable]:
    """
    Create map and reduce chains for parallel processing.

    Args:
        map_template: Template for map step
        reduce_template: Template for reduce step
        model_name: Optional model name override

    Returns:
        Dictionary with 'map' and 'reduce' chains

    Example:
        >>> chains = create_map_reduce_chain(
        ...     map_template="Summarize this chunk: {text}",
        ...     reduce_template="Combine these summaries: {summaries}"
        ... )
        >>> # Use chains['map'] for each chunk, then chains['reduce'] for final result
    """
    map_chain = create_simple_chain(map_template, model_name=model_name)
    reduce_chain = create_simple_chain(reduce_template, model_name=model_name)

    logger.debug("map_reduce_chain_created")

    return {
        "map": map_chain,
        "reduce": reduce_chain,
    }


def create_chain_with_fallback(
    primary_chain: Runnable,
    fallback_chain: Runnable,
) -> Runnable:
    """
    Create a chain with fallback for error handling.

    Args:
        primary_chain: Primary chain to try first
        fallback_chain: Fallback chain if primary fails

    Returns:
        Chain with fallback

    Example:
        >>> primary = create_chat_chain(system_message="Be technical", ...)
        >>> fallback = create_chat_chain(system_message="Be simple", ...)
        >>> chain = create_chain_with_fallback(primary, fallback)
    """
    chain = primary_chain.with_fallbacks([fallback_chain])

    logger.debug("fallback_chain_created")

    return chain


class BaseChainBuilder:
    """
    Builder class for creating chains with a fluent interface.

    Example:
        >>> chain = (
        ...     BaseChainBuilder()
        ...     .with_system_message("You are helpful")
        ...     .with_template("Answer: {question}")
        ...     .with_model("gpt-4")
        ...     .build()
        ... )
    """

    def __init__(self):
        """Initialize chain builder."""
        self.system_message: Optional[str] = None
        self.template: Optional[str] = None
        self.model_name: Optional[str] = None
        self.input_variables: Optional[List[str]] = None

    def with_system_message(self, message: str) -> "BaseChainBuilder":
        """Set system message."""
        self.system_message = message
        return self

    def with_template(self, template: str) -> "BaseChainBuilder":
        """Set prompt template."""
        self.template = template
        return self

    def with_model(self, model_name: str) -> "BaseChainBuilder":
        """Set model name."""
        self.model_name = model_name
        return self

    def with_input_variables(self, variables: List[str]) -> "BaseChainBuilder":
        """Set input variables."""
        self.input_variables = variables
        return self

    def build(self) -> Runnable:
        """
        Build the chain.

        Returns:
            Runnable chain

        Raises:
            ValueError: If template is not set
        """
        if not self.template:
            raise ValueError("Template is required")

        if self.system_message:
            return create_chat_chain(
                system_message=self.system_message,
                human_message_template=self.template,
                model_name=self.model_name,
            )
        else:
            return create_simple_chain(
                template=self.template,
                input_variables=self.input_variables,
                model_name=self.model_name,
            )
