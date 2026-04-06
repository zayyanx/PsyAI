"""
Conversational chains with memory support.

This module provides chains for multi-turn conversations with context.
"""

from typing import Any, Dict, List, Optional

try:
    from langchain.chains import ConversationChain
    from langchain.memory import (
        ConversationBufferMemory,
        ConversationBufferWindowMemory,
        ConversationSummaryMemory,
    )
except ImportError:
    # For newer LangChain versions
    ConversationChain = None  # type: ignore
    ConversationBufferMemory = None  # type: ignore
    ConversationBufferWindowMemory = None  # type: ignore
    ConversationSummaryMemory = None  # type: ignore

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableWithMessageHistory

from psyai.core.logging import get_logger
from psyai.platform.langchain_integration.client import get_langchain_client

logger = get_logger(__name__)


def create_conversational_chain(
    system_message: str = "You are a helpful AI assistant.",
    memory_type: str = "buffer",
    max_messages: Optional[int] = None,
    model_name: Optional[str] = None,
) -> Runnable:
    """
    Create a conversational chain with memory.

    Args:
        system_message: System message for context
        memory_type: Type of memory ("buffer", "window", "summary")
        max_messages: Max messages to keep (for "window" memory)
        model_name: Optional model name override

    Returns:
        Conversational chain with memory

    Example:
        >>> chain = create_conversational_chain()
        >>> response1 = await chain.ainvoke({"input": "My name is Alice"})
        >>> response2 = await chain.ainvoke({"input": "What's my name?"})
        >>> # response2 will remember "Alice"
    """
    client = get_langchain_client(model_name=model_name)

    # Create memory based on type
    if memory_type == "buffer":
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
        )
    elif memory_type == "window":
        memory = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="history",
            k=max_messages or 10,
        )
    elif memory_type == "summary":
        memory = ConversationSummaryMemory(
            llm=client.llm,
            return_messages=True,
            memory_key="history",
        )
    else:
        raise ValueError(f"Invalid memory type: {memory_type}")

    # Create prompt with memory placeholder
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    # Create chain
    chain = ConversationChain(
        llm=client.llm,
        memory=memory,
        prompt=prompt,
        verbose=False,
    )

    logger.debug(
        "conversational_chain_created",
        memory_type=memory_type,
        max_messages=max_messages,
    )

    return chain


def create_chat_memory(
    session_id: str,
    messages: Optional[List[BaseMessage]] = None,
) -> ChatMessageHistory:
    """
    Create a chat message history for a session.

    Args:
        session_id: Unique session identifier
        messages: Optional initial messages

    Returns:
        ChatMessageHistory instance

    Example:
        >>> memory = create_chat_memory("session-123")
        >>> memory.add_user_message("Hello!")
        >>> memory.add_ai_message("Hi there!")
    """
    history = ChatMessageHistory(messages=messages or [])

    logger.debug("chat_memory_created", session_id=session_id)

    return history


def create_chain_with_history(
    chain: Runnable,
    get_session_history: callable,
    input_messages_key: str = "input",
    history_messages_key: str = "history",
) -> RunnableWithMessageHistory:
    """
    Wrap a chain with message history management.

    Args:
        chain: Base chain to wrap
        get_session_history: Function to get history for a session ID
        input_messages_key: Key for input messages
        history_messages_key: Key for history messages

    Returns:
        Chain with message history

    Example:
        >>> def get_history(session_id: str):
        ...     return create_chat_memory(session_id)
        >>>
        >>> chain = create_simple_chain("Answer: {input}")
        >>> chain_with_history = create_chain_with_history(chain, get_history)
        >>> response = await chain_with_history.ainvoke(
        ...     {"input": "Hello"},
        ...     config={"configurable": {"session_id": "abc123"}}
        ... )
    """
    wrapped_chain = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key=input_messages_key,
        history_messages_key=history_messages_key,
    )

    logger.debug("chain_with_history_created")

    return wrapped_chain


class ConversationManager:
    """
    Manager for handling multi-turn conversations.

    Example:
        >>> manager = ConversationManager(session_id="user-123")
        >>> response1 = await manager.send_message("Hello!")
        >>> response2 = await manager.send_message("What's my name?")
        >>> history = manager.get_history()
    """

    def __init__(
        self,
        session_id: str,
        system_message: str = "You are a helpful AI assistant.",
        max_messages: Optional[int] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize conversation manager.

        Args:
            session_id: Unique session identifier
            system_message: System message for context
            max_messages: Max messages to keep in memory
            model_name: Optional model name override
        """
        self.session_id = session_id
        self.system_message = system_message
        self.max_messages = max_messages

        # Create chain with memory
        self.chain = create_conversational_chain(
            system_message=system_message,
            memory_type="window" if max_messages else "buffer",
            max_messages=max_messages,
            model_name=model_name,
        )

        logger.info("conversation_manager_created", session_id=session_id)

    async def send_message(self, message: str) -> str:
        """
        Send a message and get response.

        Args:
            message: User message

        Returns:
            AI response

        Example:
            >>> response = await manager.send_message("Hello!")
        """
        logger.debug(
            "conversation_message_sent",
            session_id=self.session_id,
            message_length=len(message),
        )

        response = await self.chain.ainvoke({"input": message})

        # Extract response text
        if isinstance(response, dict):
            result = response.get("response", str(response))
        else:
            result = str(response)

        logger.info(
            "conversation_message_received",
            session_id=self.session_id,
            response_length=len(result),
        )

        return result

    def get_history(self) -> List[BaseMessage]:
        """
        Get conversation history.

        Returns:
            List of messages in the conversation

        Example:
            >>> history = manager.get_history()
            >>> for msg in history:
            ...     print(f"{msg.type}: {msg.content}")
        """
        memory = self.chain.memory
        return memory.chat_memory.messages

    def clear_history(self) -> None:
        """
        Clear conversation history.

        Example:
            >>> manager.clear_history()
        """
        self.chain.memory.clear()

        logger.info("conversation_history_cleared", session_id=self.session_id)

    def add_context(self, context: str) -> None:
        """
        Add context to the conversation as a system message.

        Args:
            context: Context to add

        Example:
            >>> manager.add_context("The user prefers technical explanations")
        """
        self.chain.memory.chat_memory.add_message(SystemMessage(content=context))

        logger.debug(
            "conversation_context_added",
            session_id=self.session_id,
            context_length=len(context),
        )
