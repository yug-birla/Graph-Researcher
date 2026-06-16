
from pydantic import BaseModel, Field
from typing import Optional


class CreateLocalUserRequest(BaseModel):
    email: str
    name: Optional[str] = None
    role: str = Field(default="user")


class RegisterDocumentRequest(BaseModel):
    document_id: str
    source_file_name: Optional[str] = None
    owner_user_id: Optional[str] = None


class CreateConversationRequest(BaseModel):
    owner_user_id: Optional[str] = None
    document_id: Optional[str] = None
    title: str = "New chat"


class AddMessageRequest(BaseModel):
    conversation_id: str
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
