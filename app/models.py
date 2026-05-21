from typing import List, Literal
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's question")


class ChatMessage(BaseModel):
    role: Literal["human", "ai"]
    content: str = Field(..., min_length=1, description="Content of the message")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's question")
    chat_history: List[ChatMessage] = Field(
        default_factory=list, description="List of previous chat messages"
    )

class SessionChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's question")
    
class SessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the chat session")
    message: str = Field(..., description="Response message from the AI")
    