"""
Concrete implementations of LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
"""

from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai

from app.core.config import settings
from app.ai.base import LLMProvider, AIMessage, AIResponse, AITool
from app.db.models import ConversationMessage, MessageRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI provider (GPT-4, GPT-3.5-turbo, etc.)."""

    def __init__(
        self, api_key: Optional[str] = None, default_model: Optional[str] = None
    ):
        api_key = api_key or settings.openai_api_key
        default_model = default_model or settings.default_ai_model_openai

        if not api_key:
            raise ValueError("OpenAI API key not configured")

        super().__init__(api_key, default_model)
        self.client = AsyncOpenAI(api_key=api_key)

    def get_provider_name(self) -> str:
        return "openai"

    async def send_message(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[AITool]] = None,
        **kwargs,
    ) -> AIResponse:
        """Send message to OpenAI API."""
        model = model or self.default_model

        # Convert AIMessage to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        try:
            # Prepare request params
            request_params = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters,
                        },
                    }
                    for tool in tools
                ]

            response = await self.client.chat.completions.create(**request_params)

            return AIResponse(
                content=response.choices[0].message.content or "",
                provider=self.get_provider_name(),
                model=model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                metadata={"response_id": response.id},
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """Rough estimate: ~4 chars per token."""
        return len(text) // 4


class AnthropicProvider(LLMProvider):
    """Anthropic provider (Claude 3.x)."""

    def __init__(
        self, api_key: Optional[str] = None, default_model: Optional[str] = None
    ):
        api_key = api_key or settings.anthropic_api_key
        default_model = default_model or settings.default_ai_model_anthropic

        if not api_key:
            raise ValueError("Anthropic API key not configured")

        super().__init__(api_key, default_model)
        self.client = AsyncAnthropic(api_key=api_key)

    def get_provider_name(self) -> str:
        return "anthropic"

    async def send_message(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[AITool]] = None,
        **kwargs,
    ) -> AIResponse:
        """Send message to Anthropic API."""
        model = model or self.default_model

        # Anthropic requires system message separate
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append(
                    {"role": msg.role, "content": msg.content}
                )

        try:
            request_params = {
                "model": model,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if system_message:
                request_params["system"] = system_message

            # Add tools if provided
            if tools:
                request_params["tools"] = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.parameters,
                    }
                    for tool in tools
                ]

            response = await self.client.messages.create(**request_params)

            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            return AIResponse(
                content=content,
                provider=self.get_provider_name(),
                model=model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                metadata={"response_id": response.id},
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """Rough estimate: ~4 chars per token."""
        return len(text) // 4


class GoogleProvider(LLMProvider):
    """Google provider (Gemini)."""

    def __init__(
        self, api_key: Optional[str] = None, default_model: Optional[str] = None
    ):
        api_key = api_key or settings.google_api_key
        default_model = default_model or settings.default_ai_model_google

        if not api_key:
            raise ValueError("Google API key not configured")

        super().__init__(api_key, default_model)
        genai.configure(api_key=api_key)

    def get_provider_name(self) -> str:
        return "google"

    async def send_message(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        tools: Optional[List[AITool]] = None,
        **kwargs,
    ) -> AIResponse:
        """Send message to Google Gemini API."""
        model = model or self.default_model

        # Google Gemini format
        gemini_model = genai.GenerativeModel(model)

        # Build conversation history
        chat_history = []
        for msg in messages:
            if msg.role == "system":
                # Prepend system message to first user message
                continue
            role = "user" if msg.role in ["user", "system"] else "model"
            chat_history.append({"role": role, "parts": [msg.content]})

        try:
            # Start chat with history
            chat = gemini_model.start_chat(history=chat_history[:-1])

            # Send last message
            last_message = messages[-1].content
            response = await chat.send_message_async(
                last_message,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )

            return AIResponse(
                content=response.text,
                provider=self.get_provider_name(),
                model=model,
                tokens_used=0,  # Google doesn't provide token count in response
                finish_reason="stop",
                metadata={},
            )

        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """Rough estimate: ~4 chars per token."""
        return len(text) // 4


# Provider registry
PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
}


def get_provider(
    provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None
) -> LLMProvider:
    """
    Get a provider instance by name.

    Args:
        provider_name: Name of the provider ("openai", "anthropic", "google")
        api_key: Optional API key override
        model: Optional model override

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider name is invalid
    """
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown provider: {provider_name}. Available: {list(PROVIDERS.keys())}"
        )

    return provider_class(api_key=api_key, default_model=model)


async def get_ai_response(
    conversation_id: int,
    message: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    db: AsyncSession = None,
) -> Dict[str, Any]:
    """
    Get an AI response and store it in the database.

    Args:
        conversation_id: Conversation ID
        message: User message
        provider: Provider name (defaults to config)
        model: Model name (defaults to provider default)
        db: Database session

    Returns:
        Response dictionary
    """
    provider = provider or settings.default_ai_provider

    # Get conversation history
    query = (
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at)
    )
    result = await db.execute(query)
    history = result.scalars().all()

    # Build messages list
    messages = []

    # Add system prompt (load from prompts table or file)
    system_prompt = """You are an AI assistant specializing in macroeconomics, precious metals markets, and the gold–silver ratio (GSR).
You have access to historical and real-time data about gold, silver, the GSR, macroeconomic indicators, and derived metrics.
Your primary goal is to help the user understand current conditions, regimes, and tradeoffs in using the GSR to accumulate more ounces of gold and manage risk over time.

You must:
- Be precise, transparent, and conservative in your reasoning.
- Clearly separate facts, data-driven conclusions, and speculation.
- Explain your reasoning step by step in plain language.
- Emphasize risk management, position sizing, and uncertainty.
- Never present anything as guaranteed or certain.
- Never give personalized investment, tax, or legal advice."""

    messages.append(AIMessage(role="system", content=system_prompt))

    # Add conversation history
    for msg in history:
        messages.append(AIMessage(role=msg.role.value, content=msg.content))

    # Get provider and send message
    try:
        llm_provider = get_provider(provider, model=model)
        response = await llm_provider.send_message(
            messages,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
        )

        # Store assistant response
        assistant_message = ConversationMessage(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response.content,
            provider=provider,
            model_name=response.model,
            tokens_used=response.tokens_used,
        )
        db.add(assistant_message)
        await db.commit()

        return {
            "conversation_id": conversation_id,
            "message": {"role": "assistant", "content": response.content},
            "provider": provider,
            "model": response.model,
            "tokens_used": response.tokens_used,
            "timestamp": response.timestamp,
        }

    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        raise
