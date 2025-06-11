from typing import Dict, Any

from sqlalchemy.orm import Session
from . import models, schemas, auth


def create_user(db: Session, user: schemas.UserCreate):
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_task(db: Session, task: schemas.TaskCreate, current_user: models.User):
    db_task = models.Task(
        **task.model_dump(),
        creator_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, fields_to_update: Dict[str, Any]):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None  # Или выбросьте исключение

    for key, value in fields_to_update.items():
        if hasattr(task, key):
            setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session, current_user: models.User):
    return db.query(models.Task).filter(models.Task.creator_id == current_user.id).all()


def get_all_tasks(db: Session):
    return db.query(models.Task).all()


def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()


def assign_responsible(db: Session, task_id: int, user_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None  # Или выбросить исключение, если хочешь

    task.responsible_id = user_id
    db.commit()
    db.refresh(task)
    return task


def create_board(db: Session, board: schemas.BoardCreate) -> models.Board:
    db_board = models.Board(title=board.title)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


def delete_board(db: Session, board_id: int):
    board = db.query(models.Board).get(board_id)
    if board:
        db.delete(board)
        db.commit()


def update_board(db: Session, board_id: int, data: dict):
    board = db.query(models.Board).get(board_id)
    if not board:
        return None
    for key, value in data.items():
        setattr(board, key, value)
    db.commit()
    db.refresh(board)
    return board


def add_user_to_board(db: Session, board_id: int, user_id: int):
    board = db.query(models.Board).get(board_id)
    user = db.query(models.User).get(user_id)
    if board and user and user not in board.users:
        board.users.append(user)
        db.commit()
        db.refresh(board)
        return board
    return None


def remove_user_from_board(db: Session, board_id: int, user_id: int):
    board = db.query(models.Board).get(board_id)
    user = db.query(models.User).get(user_id)
    if board and user and user in board.users:
        board.users.remove(user)
        db.commit()
        db.refresh(board)
        return board
    return None

def add_task_to_board(db: Session, board_id: int, task_id: int):
    board = db.query(models.Board).filter_by(id=board_id).first()
    task = db.query(models.Task).filter_by(id=task_id).first()
    if board and task:
        board.tasks.append(task)
        db.commit()
        db.refresh(board)
        return board
    return None

def remove_task_from_board(db: Session, board_id: int, task_id: int):
    board = db.query(models.Board).filter_by(id=board_id).first()
    task = db.query(models.Task).filter_by(id=task_id).first()
    if board and task and task in board.tasks:
        board.tasks.remove(task)
        db.commit()
        db.refresh(board)
        return board
    return None