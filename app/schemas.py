from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import RoleEnum, TaskStatusEnum

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    role: RoleEnum
    manager_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    assigned_to_id: int

class TaskUpdate(BaseModel):
    status: TaskStatusEnum
    hours_spent: Optional[float]

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to_id: int
    assigned_by_id: int
    status: TaskStatusEnum
    hours_spent: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TaskHistoryResponse(BaseModel):
    id: int
    task_id: int
    updated_by_id: int
    status_before: TaskStatusEnum
    status_after: TaskStatusEnum
    hours_spent: float
    timestamp: datetime

    class Config:
        orm_mode = True
