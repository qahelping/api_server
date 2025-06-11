from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth, database
from .schemas import TaskUpdate, AssignResponsibleRequest

router = APIRouter()


@router.post("/users/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, user)


@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.LoginInput, db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/tasks", response_model=schemas.TaskOut)
def create_task(task: schemas.TaskCreate,
                current_user=Depends(auth.get_current_user),
                db: Session = Depends(database.get_db)):
    return crud.create_task(db, task, current_user)


@router.get("/tasks_by_user_id", response_model=list[schemas.TaskOut])
def read_tasks(current_user=Depends(auth.get_current_user),
               db: Session = Depends(database.get_db)):
    return crud.get_tasks(db, current_user)


@router.get("/tasks", response_model=list[schemas.TaskOut])
def read_tasks(db: Session = Depends(database.get_db)):
    return crud.get_all_tasks(db)


@router.put("/tasks/{task_id}/assign", response_model=schemas.TaskOut)
def assign_responsible_to_task(
    task_id: int,
    assign_request: AssignResponsibleRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Проверяем, что задача существует
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # (Опционально) Проверяем, что current_user имеет право менять ответственного
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to assign responsible")

    # Назначаем ответственного
    updated_task = crud.assign_responsible(db, task_id, assign_request.user_id)
    if not updated_task:
        raise HTTPException(status_code=400, detail="Failed to assign responsible")

    return updated_task


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task_route(
    task_id: int,
    task_update: TaskUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    updated_task = crud.update_task(db, task_id, task_update.dict(exclude_unset=True))
    if not updated_task:
        raise HTTPException(status_code=400, detail="Update failed")
    return updated_task


@router.post("/boards", response_model=schemas.BoardOut)
def create_board(board: schemas.Board, db: Session = Depends(database.get_db)):
    return crud.create_board(db, board)


@router.delete("/boards/{board_id}")
def delete_board(board_id: int, db: Session = Depends(database.get_db)):
    crud.delete_board(db, board_id)
    return {"detail": "Board deleted"}


@router.patch("/boards/{board_id}", response_model=schemas.BoardOut)
def update_board(board_id: int, board_data: schemas.BoardUpdate, db: Session = Depends(database.get_db)):
    board = crud.update_board(db, board_id, board_data.dict(exclude_unset=True))
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.post("/boards/{board_id}/users/add")
def add_user(board_id: int, data: schemas.BoardUserModify, db: Session = Depends(database.get_db)):
    board = crud.add_user_to_board(db, board_id, data.user_id)
    if not board:
        raise HTTPException(status_code=400, detail="User could not be added")
    return {"detail": "User added"}


@router.post("/boards/{board_id}/users/remove")
def remove_user(board_id: int, data: schemas.BoardUserModify, db: Session = Depends(database.get_db)):
    board = crud.remove_user_from_board(db, board_id, data.user_id)
    if not board:
        raise HTTPException(status_code=400, detail="User could not be removed")
    return {"detail": "User removed"}

@router.post("/boards", response_model=schemas.BoardOut)
def create_board(board_data: schemas.Board,
                 db: Session = Depends(database.get_db)):
    return crud.create_board(db, board_data.name)

@router.post("/boards/{board_id}/tasks/add")
def add_task(board_id: int, data: schemas.TaskToBoard,
             db: Session = Depends(database.get_db)):
    board = crud.add_task_to_board(db, board_id, data.task_id)
    if not board:
        raise HTTPException(status_code=400, detail="Board or task not found")
    return {"detail": "Task added to board"}

@router.post("/boards/{board_id}/tasks/remove")
def remove_task(board_id: int, data: schemas.TaskToBoard,
                db: Session = Depends(database.get_db)):
    board = crud.remove_task_from_board(db, board_id, data.task_id)
    if not board:
        raise HTTPException(status_code=400, detail="Task not removed or not found")
    return {"detail": "Task removed from board"}

@router.get("/boards/{board_id}/tasks", response_model=list[schemas.TaskOut])
def get_tasks_from_board(board_id: int, db: Session = Depends(database.get_db)):
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board.tasks