"""
Abstract base class for LLM providers.
Defines the interface that all providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AIMessage:
    """Represents a message in a conversation."""

    role: str  # "system", "user", "assistant", "tool"
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """Response from an AI provider."""

    content: str
    provider: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class AITool:
    """Represents a tool/function that the AI can call."""

    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema for parameters


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, default_model: str):
        """
        Initialize the provider.

        Args:
            api_key: API key for the provider
            default_model: Default model to use
        """
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    async def send_message(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[AITool]] = None,
        **kwargs,
    ) -> AIResponse:
        """
        Send a message and get a response.

        Args:
            messages: List of conversation messages
            model: Model to use (defaults to provider's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            tools: Optional list of tools the AI can use
            **kwargs: Additional provider-specific parameters

        Returns:
            AIResponse with the model's reply

        Raises:
            Exception: If the API call fails
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        pass

    def format_system_prompt(self, prompt: str) -> AIMessage:
        """Format a system prompt as an AIMessage."""
        return AIMessage(role="system", content=prompt)

    def format_user_message(self, content: str) -> AIMessage:
        """Format a user message as an AIMessage."""
        return AIMessage(role="user", content=content)

    def format_assistant_message(self, content: str) -> AIMessage:
        """Format an assistant message as an AIMessage."""
        return AIMessage(role="assistant", content=content)
