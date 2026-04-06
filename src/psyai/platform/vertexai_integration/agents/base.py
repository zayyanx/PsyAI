"""
Base agent templates and builders for Vertex AI.

This module provides reusable agent patterns using Vertex AI Gemini models.
"""

from typing import Any, Callable, Dict, List, Optional

from vertexai.generative_models import ChatSession, Content, Part

from psyai.core.logging import get_logger
from psyai.platform.vertexai_integration.client import get_vertexai_client

logger = get_logger(__name__)


class AgentResponse:
    """Response from an agent."""

    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize agent response.

        Args:
            content: Response content
            metadata: Optional metadata
        """
        self.content = content
        self.metadata = metadata or {}

    def __str__(self) -> str:
        return self.content


class SimpleAgent:
    """
    Simple agent for single-turn interactions.

    Example:
        >>> agent = SimpleAgent(system_instruction="You are a helpful assistant")
        >>> response = await agent.arun("What is PsyAI?")
        >>> print(response.content)
    """

    def __init__(
        self,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize simple agent.

        Args:
            system_instruction: System instruction for the agent
            model_name: Optional model name override
        """
        self.system_instruction = system_instruction
        self.client = get_vertexai_client(model_name=model_name)

        logger.debug("simple_agent_created")

    def run(self, prompt: str, **kwargs: Any) -> AgentResponse:
        """
        Run the agent with a prompt.

        Args:
            prompt: User prompt
            **kwargs: Additional generation arguments

        Returns:
            AgentResponse
        """
        full_prompt = prompt
        if self.system_instruction:
            full_prompt = f"{self.system_instruction}\n\n{prompt}"

        result = self.client.generate(full_prompt, **kwargs)
        return AgentResponse(content=result)

    async def arun(self, prompt: str, **kwargs: Any) -> AgentResponse:
        """
        Run the agent asynchronously.

        Args:
            prompt: User prompt
            **kwargs: Additional generation arguments

        Returns:
            AgentResponse
        """
        full_prompt = prompt
        if self.system_instruction:
            full_prompt = f"{self.system_instruction}\n\n{prompt}"

        result = await self.client.agenerate(full_prompt, **kwargs)
        return AgentResponse(content=result)


class ConversationalAgent:
    """
    Agent with conversation memory.

    Example:
        >>> agent = ConversationalAgent(system_instruction="You are helpful")
        >>> response1 = await agent.arun("My name is Alice")
        >>> response2 = await agent.arun("What's my name?")  # Remembers context
    """

    def __init__(
        self,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize conversational agent.

        Args:
            system_instruction: System instruction for the agent
            model_name: Optional model name override
        """
        self.system_instruction = system_instruction
        self.client = get_vertexai_client(model_name=model_name)
        self.chat: Optional[ChatSession] = None
        self._initialize_chat()

        logger.debug("conversational_agent_created")

    def _initialize_chat(self) -> None:
        """Initialize the chat session."""
        history = []
        if self.system_instruction:
            # Add system instruction as first message
            history.append(
                Content(
                    role="user",
                    parts=[Part.from_text(f"System: {self.system_instruction}")],
                )
            )
            history.append(
                Content(
                    role="model",
                    parts=[Part.from_text("Understood. I'm ready to help.")],
                )
            )

        self.chat = self.client.start_chat(history=history)

    def run(self, message: str, **kwargs: Any) -> AgentResponse:
        """
        Send a message and get a response.

        Args:
            message: User message
            **kwargs: Additional generation arguments

        Returns:
            AgentResponse
        """
        if not self.chat:
            self._initialize_chat()

        response = self.chat.send_message(message, **kwargs)
        return AgentResponse(content=response.text)

    async def arun(self, message: str, **kwargs: Any) -> AgentResponse:
        """
        Send a message asynchronously.

        Args:
            message: User message
            **kwargs: Additional generation arguments

        Returns:
            AgentResponse
        """
        if not self.chat:
            self._initialize_chat()

        response = await self.chat.send_message_async(message, **kwargs)
        return AgentResponse(content=response.text)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._initialize_chat()
        logger.debug("conversation_history_cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.

        Returns:
            List of message dictionaries
        """
        if not self.chat:
            return []

        history = []
        for content in self.chat.history:
            history.append(
                {
                    "role": content.role,
                    "content": "".join(
                        [part.text for part in content.parts if hasattr(part, "text")]
                    ),
                }
            )

        return history


class FunctionCallingAgent:
    """
    Agent with function calling capabilities.

    Example:
        >>> def get_weather(location: str) -> str:
        ...     return f"Weather in {location}: Sunny"
        >>>
        >>> agent = FunctionCallingAgent(
        ...     functions=[get_weather],
        ...     system_instruction="You help with weather queries"
        ... )
        >>> response = await agent.arun("What's the weather in NYC?")
    """

    def __init__(
        self,
        functions: List[Callable],
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize function calling agent.

        Args:
            functions: List of callable functions
            system_instruction: System instruction for the agent
            model_name: Optional model name override
        """
        self.functions = {func.__name__: func for func in functions}
        self.system_instruction = system_instruction
        self.client = get_vertexai_client(model_name=model_name)

        logger.debug("function_calling_agent_created", function_count=len(functions))

    def run(self, prompt: str, **kwargs: Any) -> AgentResponse:
        """
        Run the agent with function calling.

        Args:
            prompt: User prompt
            **kwargs: Additional generation arguments

        Returns:
            AgentResponse
        """
        # Build full prompt with system instruction
        full_prompt = prompt
        if self.system_instruction:
            full_prompt = f"{self.system_instruction}\n\n{prompt}"

        # Add function descriptions to prompt
        func_descriptions = self._build_function_descriptions()
        if func_descriptions:
            full_prompt += f"\n\nAvailable functions:\n{func_descriptions}"

        result = self.client.generate(full_prompt, **kwargs)
        return AgentResponse(content=result)

    async def arun(self, prompt: str, **kwargs: Any) -> AgentResponse:
        """
        Run the agent asynchronously with function calling.

        Args:
            prompt: User prompt
            **kwargs: Additional generation arguments

        Returns:
            AgentResponse
        """
        # Build full prompt with system instruction
        full_prompt = prompt
        if self.system_instruction:
            full_prompt = f"{self.system_instruction}\n\n{prompt}"

        # Add function descriptions to prompt
        func_descriptions = self._build_function_descriptions()
        if func_descriptions:
            full_prompt += f"\n\nAvailable functions:\n{func_descriptions}"

        result = await self.client.agenerate(full_prompt, **kwargs)
        return AgentResponse(content=result)

    def _build_function_descriptions(self) -> str:
        """
        Build function descriptions for the prompt.

        Returns:
            String with function descriptions
        """
        descriptions = []
        for name, func in self.functions.items():
            doc = func.__doc__ or "No description"
            descriptions.append(f"- {name}: {doc.strip()}")

        return "\n".join(descriptions)


class AgentBuilder:
    """
    Builder class for creating agents with a fluent interface.

    Example:
        >>> agent = (
        ...     AgentBuilder()
        ...     .with_system_instruction("You are helpful")
        ...     .with_model("gemini-1.5-pro")
        ...     .build()
        ... )
    """

    def __init__(self) -> None:
        """Initialize agent builder."""
        self.system_instruction: Optional[str] = None
        self.model_name: Optional[str] = None
        self.agent_type: str = "simple"
        self.functions: List[Callable] = []

    def with_system_instruction(self, instruction: str) -> "AgentBuilder":
        """Set system instruction."""
        self.system_instruction = instruction
        return self

    def with_model(self, model_name: str) -> "AgentBuilder":
        """Set model name."""
        self.model_name = model_name
        return self

    def with_conversation(self) -> "AgentBuilder":
        """Make agent conversational."""
        self.agent_type = "conversational"
        return self

    def with_functions(self, functions: List[Callable]) -> "AgentBuilder":
        """Add function calling capabilities."""
        self.functions = functions
        self.agent_type = "function_calling"
        return self

    def build(self) -> Any:
        """
        Build the agent.

        Returns:
            Agent instance

        Raises:
            ValueError: If configuration is invalid
        """
        if self.agent_type == "conversational":
            return ConversationalAgent(
                system_instruction=self.system_instruction,
                model_name=self.model_name,
            )
        elif self.agent_type == "function_calling":
            if not self.functions:
                raise ValueError("Functions required for function calling agent")
            return FunctionCallingAgent(
                functions=self.functions,
                system_instruction=self.system_instruction,
                model_name=self.model_name,
            )
        else:
            return SimpleAgent(
                system_instruction=self.system_instruction,
                model_name=self.model_name,
            )
