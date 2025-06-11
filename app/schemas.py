from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoginInput(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    status: str
    responsible_id: int


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


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    responsible_id: Optional[int] = None


class AssignResponsibleRequest(BaseModel):
    user_id: int


class Board(BaseModel):
    title: str


class BoardUpdate(BaseModel):
    title: Optional[str] = None


class BoardOut(Board):
    id: int

    class Config:
        from_attributes = True


class BoardUserModify(BaseModel):
    user_id: int


class TaskToBoard(BaseModel):
    task_id: int

class BoardCreate(BaseModel):
    title: str