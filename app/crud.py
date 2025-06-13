from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from . import models, schemas, auth


def update_fields(instance, data: Dict[str, Any]):
    for key, value in data.items():
        if hasattr(instance, key):
            setattr(instance, key, value)


def create_user(db: Session, user: schemas.UserCreate):
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).get(user_id)


def get_all_users(db: Session):
    return db.query(models.User).all()


def update_user(db: Session, user_id: int, update_data: dict):
    user = get_user(db, user_id)
    if not user:
        return None
    update_fields(user, update_data)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def update_user_avatar(db: Session, user_id: int, avatar_url: str):
    return update_user(db, user_id, {"avatar_url": avatar_url})


def create_task(db: Session, task: schemas.TaskCreate, current_user: models.User):
    db_task = models.Task(**task.model_dump(), creator_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int):
    return db.query(models.Task).get(task_id)


def get_all_tasks(db: Session):
    return db.query(models.Task).all()


def get_tasks(db: Session, current_user: models.User):
    return db.query(models.Task).filter_by(creator_id=current_user.id).all()


def update_task(db: Session, task_id: int, fields_to_update: Dict[str, Any]):
    task = get_task(db, task_id)
    if not task:
        return None
    update_fields(task, fields_to_update)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int):
    task = get_task(db, task_id)
    if task:
        db.delete(task)
        db.commit()


def assign_responsible(db: Session, task_id: int, user_id: int):
    return update_task(db, task_id, {"responsible_id": user_id})


def update_task_pdf(db: Session, task_id: int, pdf_path: str):
    return update_task(db, task_id, {"pdf_path": pdf_path})


def remove_task_pdf(db: Session, task_id: int):
    return update_task(db, task_id, {"pdf_path": None})


def create_board(db: Session, board: schemas.BoardBase):
    db_board = models.Board(title=board.title)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


def get_board(db: Session, board_id: int):
    return db.query(models.Board).get(board_id)


def get_board_by_name(db: Session, name: str):
    return db.query(models.Board).filter_by(title=name).first()


def update_board(db: Session, board_id: int, data: dict):
    board = get_board(db, board_id)
    if not board:
        return None
    update_fields(board, data)
    db.commit()
    db.refresh(board)
    return board


def delete_board(db: Session, board_id: int):
    board = get_board(db, board_id)
    if board:
        db.delete(board)
        db.commit()


def add_user_to_board(db: Session, board_id: int, user_id: int):
    board, user = get_board(db, board_id), get_user(db, user_id)
    if board and user and user not in board.users:
        board.users.append(user)
        db.commit()
        db.refresh(board)
        return board
    return None


def remove_user_from_board(db: Session, board_id: int, user_id: int):
    board, user = get_board(db, board_id), get_user(db, user_id)
    if board and user and user in board.users:
        board.users.remove(user)
        db.commit()
        db.refresh(board)
        return board
    return None


def add_task_to_board(db: Session, board_id: int, task_id: int):
    board, task = get_board(db, board_id), get_task(db, task_id)
    if board and task and task not in board.tasks:
        board.tasks.append(task)
        db.commit()
        db.refresh(board)
        return board
    return None


def remove_task_from_board(db: Session, board_id: int, task_id: int):
    board, task = get_board(db, board_id), get_task(db, task_id)
    if board and task and task in board.tasks:
        board.tasks.remove(task)
        db.commit()
        db.refresh(board)
        return board
    return None

