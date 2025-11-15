"""AI Advisor API endpoints - chat with multi-provider LLM."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.db.models import Conversation, ConversationMessage, MessageRole


router = APIRouter()


# Pydantic schemas
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    provider: Optional[str] = None  # "openai", "anthropic", "google"
    model: Optional[str] = None
    context_type: Optional[str] = "general"
    include_data_context: bool = True


class ChatResponse(BaseModel):
    conversation_id: int
    message: ChatMessage
    provider: str
    model: str
    tokens_used: int
    timestamp: datetime


class MultiProviderChatRequest(BaseModel):
    message: str
    providers: List[str]  # ["openai", "anthropic", "google"]
    context_type: Optional[str] = "general"


class ConversationResponse(BaseModel):
    id: int
    context_type: Optional[str] = None
    created_at: datetime
    message_count: int

    class Config:
        from_attributes = True


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message to the AI advisor and get a response."""
    # Get or create conversation
    if request.conversation_id:
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(context_type=request.context_type)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Store user message
    user_message = ConversationMessage(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_message)

    # This will call the AI service to get response
    # For now, return a placeholder
    from app.ai.providers import get_ai_response

    ai_response = await get_ai_response(
        conversation_id=conversation.id,
        message=request.message,
        provider=request.provider,
        model=request.model,
        db=db,
    )

    return ai_response


@router.post("/chat/multi-provider")
async def chat_multi_provider(
    request: MultiProviderChatRequest, db: AsyncSession = Depends(get_db)
):
    """Send same message to multiple AI providers and get all responses."""
    responses = []

    for provider in request.providers:
        chat_req = ChatRequest(
            message=request.message,
            provider=provider,
            context_type=request.context_type,
        )
        response = await chat(chat_req, db)
        responses.append(response)

    return {"responses": responses}


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    context_type: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List conversation history."""
    query = select(Conversation)

    if context_type:
        query = query.where(Conversation.context_type == context_type)

    query = query.order_by(Conversation.created_at.desc()).limit(limit)

    result = await db.execute(query)
    conversations = result.scalars().all()

    # Count messages for each conversation
    response = []
    for conv in conversations:
        msg_result = await db.execute(
            select(ConversationMessage).where(
                ConversationMessage.conversation_id == conv.id
            )
        )
        message_count = len(msg_result.scalars().all())

        response.append(
            ConversationResponse(
                id=conv.id,
                context_type=conv.context_type,
                created_at=conv.created_at,
                message_count=message_count,
            )
        )

    return response


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int, db: AsyncSession = Depends(get_db)
):
    """Get all messages in a conversation."""
    query = (
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at)
    )

    result = await db.execute(query)
    messages = result.scalars().all()

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": msg.role.value,
                "content": msg.content,
                "provider": msg.provider,
                "model_name": msg.model_name,
                "tokens_used": msg.tokens_used,
                "created_at": msg.created_at,
            }
            for msg in messages
        ],
    }


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a conversation and all its messages."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()
