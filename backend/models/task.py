from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    DEAD = "DEAD"  # exhausted all retries


class TaskCreate(BaseModel):
    """What the user sends when submitting a task"""
    task_type: str = Field(..., example="send_email")
    payload: Dict[str, Any] = Field(..., example={"to": "user@gmail.com", "subject": "Hello"})
    priority: int = Field(default=5, ge=1, le=10, description="1=lowest, 10=highest")
    max_retries: int = Field(default=3, ge=0, le=10)


class TaskResponse(BaseModel):
    """What we return to the user"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    status: TaskStatus
    priority: int
    max_retries: int
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True