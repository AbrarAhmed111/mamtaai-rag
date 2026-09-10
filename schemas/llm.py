"""
Pydantic models for LLM interactions: Chat, Streaming, Extraction, and Embeddings.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Represents a single message in a chat conversation."""
    role: Literal["system", "user", "assistant", "developer"] = Field(
        default="user",
        description="Role of the message sender"
    )
    content: str = Field(
        ...,
        description="Text content of the message"
    )


class ChatRequest(BaseModel):
    """Payload for chat completions."""
    messages: List[ChatMessage] = Field(
        ...,
        min_length=1,
        description="List of messages representing the conversation history"
    )
    model: Optional[str] = Field(
        None,
        description="LLM model identifier. If omitted, the default from settings is used."
    )
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature between 0.0 and 2.0"
    )
    max_tokens: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum tokens to generate in the completion"
    )
    system_prompt: Optional[str] = Field(
        None,
        description="Optional system prompt to prepend if not already in messages"
    )


class UsageInfo(BaseModel):
    """Token usage details."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """Response payload for chat completions."""
    id: str = Field(..., description="Unique completion ID")
    model: str = Field(..., description="Model used for generation")
    role: str = Field(default="assistant", description="Role of the responder")
    content: str = Field(..., description="Generated message content")
    finish_reason: Optional[str] = Field(None, description="Reason the model stopped generation")
    usage: Optional[UsageInfo] = Field(None, description="Token usage statistics")


class QuickPromptRequest(BaseModel):
    """Simple one-shot prompt request without full conversation history."""
    prompt: str = Field(..., min_length=1, description="The user prompt or query")
    system_prompt: Optional[str] = Field(None, description="Optional system instruction")
    model: Optional[str] = Field(None, description="Optional model override")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)


class StructuredExtractionRequest(BaseModel):
    """Request to extract structured data from unstructured text."""
    text: str = Field(..., min_length=1, description="The raw text to analyze and extract from")
    instructions: Optional[str] = Field(
        None,
        description="Specific extraction instructions or context"
    )
    model: Optional[str] = Field(None, description="Optional model override")


class EntityExtractionItem(BaseModel):
    """Example entity item for demonstration."""
    name: str = Field(..., description="Entity name or title")
    category: str = Field(..., description="Type or category (e.g. Person, Organization, Location, Concept)")
    details: Optional[str] = Field(None, description="Brief description or context")


class StructuredEntitiesResponse(BaseModel):
    """Example structured extraction response."""
    summary: str = Field(..., description="High-level summary of the input text")
    sentiment: Literal["positive", "neutral", "negative", "mixed"] = Field(
        default="neutral",
        description="Overall sentiment detected"
    )
    entities: List[EntityExtractionItem] = Field(
        default_factory=list,
        description="List of extracted entities"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Bullet points of main takeaways"
    )


class EmbeddingRequest(BaseModel):
    """Request payload for generating vector embeddings."""
    input: Union[str, List[str]] = Field(
        ...,
        description="Single text string or array of strings to embed"
    )
    model: Optional[str] = Field(
        None,
        description="Embedding model name. Defaults to configured setting."
    )


class EmbeddingItem(BaseModel):
    """A single embedding vector result."""
    index: int
    embedding: List[float]


class EmbeddingResponse(BaseModel):
    """Response payload containing generated vector embeddings."""
    model: str
    embeddings: List[List[float]]
    dimensions: int
    total_tokens: int = 0
