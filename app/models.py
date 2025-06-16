from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    avatar_url = Column(String, nullable=True)
    role = Column(String, default='user')
    closed_tasks_count = Column(Integer, default=0)

    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    responsible_tasks = relationship("Task", back_populates="responsible", foreign_keys="Task.responsible_id")

    boards = relationship("Board", secondary="board_users", back_populates="users")  # ← вот это важно!

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    pdf_path = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    responsible_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True)

    creator = relationship("User", back_populates="created_tasks", foreign_keys=[creator_id])
    responsible = relationship("User", back_populates="responsible_tasks", foreign_keys=[responsible_id])
    board = relationship("Board", back_populates="tasks")


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")
    users = relationship("User", secondary="board_users", back_populates="boards")


class BoardUser(Base):
    __tablename__ = "board_users"

    board_id = Column(Integer, ForeignKey("boards.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
