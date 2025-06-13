from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Аутентификация ---
class LoginInput(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Задачи ---
class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    status: str
    responsible_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    responsible_id: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    created_at: datetime
    responsible_id: int
    creator_id: int

    class Config:
        from_attributes = True


class AssignResponsibleRequest(BaseModel):
    user_id: int


# --- Доски ---
class BoardBase(BaseModel):
    title: str


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    title: Optional[str] = None


class BoardOut(BoardBase):
    id: int

    class Config:
        from_attributes = True


class BoardUserModify(BaseModel):
    user_id: int


class TaskToBoard(BaseModel):
    task_id: int
