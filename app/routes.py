import os
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette import status

from . import crud, models, schemas, auth, database
from .auth import get_password_hash
from .schemas import TaskUpdate, AssignResponsibleRequest

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # папка с файлом кода
AVATAR_DIR = os.path.join(BASE_DIR, "static", "avatars")
PDF_DIR = os.path.join(BASE_DIR, "static", "pdfs")

os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/admin/create", response_model=schemas.UserOut)
def create_admin_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(database.get_db),
):
    db_user = auth.get_user(db, user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        role="admin"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/users/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    created_user = crud.create_user(db, user)

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )
    return created_user


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

    # Проверяем, что current_user имеет право менять ответственного
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to assign responsible")

    # Проверяем, что новый ответственный существует
    new_responsible = crud.get_user(db, assign_request.user_id)
    if not new_responsible:
        raise HTTPException(status_code=404, detail="Responsible user not found")

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


@router.delete("/boards/{board_id}")
def delete_board(board_id: int,
                 current_user: models.User = Depends(auth.get_current_user),
                 db: Session = Depends(database.get_db), ):
    # Проверяем, что доска существует перед удалением
    board = crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Удалять пользователей может только администратор"
        )

    result = crud.delete_board(db, board_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete board")
    return {"detail": "Board deleted"}


@router.patch("/boards/{board_id}", response_model=schemas.BoardOut)
def update_board(board_id: int, board_data: schemas.BoardBase, db: Session = Depends(database.get_db)):
    # Проверяем, что доска существует
    board = crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Проверяем, что новое имя не конфликтует с существующими досками
    if board_data.title:
        existing_board = crud.get_board_by_name(db, board_data.title)
        if existing_board and existing_board.id != board_id:
            raise HTTPException(status_code=400, detail="Board with this name already exists")

    updated_board = crud.update_board(db, board_id, board_data.dict(exclude_unset=True))
    if not updated_board:
        raise HTTPException(status_code=400, detail="Update failed")
    return updated_board


@router.post("/boards/{board_id}/users/add")
def add_user(board_id: int, data: schemas.BoardUserModify,
             current_user: models.User = Depends(auth.get_current_user),
             db: Session = Depends(database.get_db)):
    # Проверяем, что доска существует
    board = crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if board.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="User can not update board")

    # Проверяем, что пользователь существует
    user_to_add = crud.get_user(db, data.user_id)
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, что пользователь уже не добавлен в доску
    if user_to_add in board.users:
        raise HTTPException(status_code=400, detail="User already in board")

    board = crud.add_user_to_board(db, board_id, data.user_id)
    if not board:
        raise HTTPException(status_code=400, detail="User could not be added")
    return {"detail": "User added"}


@router.post("/boards/{board_id}/users/remove")
def remove_user(board_id: int, data: schemas.BoardUserModify,
                current_user: models.User = Depends(auth.get_current_user),
                db: Session = Depends(database.get_db)):
    # Проверяем, что доска существует
    board = crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if board.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="User can not remove other user")

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Удалять пользователей может только администратор"
        )

    # Проверяем, что пользователь существует
    user_to_remove = crud.get_user(db, data.user_id)
    if not user_to_remove:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, что пользователь действительно в доске
    if user_to_remove not in board.users:
        raise HTTPException(status_code=400, detail="User not in board")

    board = crud.remove_user_from_board(db, board_id, data.user_id)
    if not board:
        raise HTTPException(status_code=400, detail="User could not be removed")
    return {"detail": "User removed"}


@router.post("/boards", response_model=schemas.BoardOut)
def create_board(board_data: schemas.BoardBase,
                 current_user: models.User = Depends(auth.get_current_user),
                 db: Session = Depends(database.get_db)):
    # Проверяем, что доска с таким именем не существует
    existing_board = crud.get_board_by_name(db, board_data.title)
    if existing_board:
        raise HTTPException(status_code=400, detail="Board with this name already exists")

    return crud.create_board(db, board_data)


@router.get("/boards/{board_id}", response_model=schemas.BoardOut)
def read_board(board_id: int, db: Session = Depends(database.get_db)):
    board = crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.post("/boards/{board_id}/tasks/add")
def add_task(board_id: int, data: schemas.TaskToBoard,
             current_user: models.User = Depends(auth.get_current_user),
             db: Session = Depends(database.get_db)):
    # Проверяем, что доска существует
    board = crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Проверяем, что задача существует
    task = crud.get_task(db, data.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем, что задача уже не в доске
    if task in board.tasks:
        raise HTTPException(status_code=400, detail="Task already in board")

    board = crud.add_task_to_board(db, board_id, data.task_id)
    if not board:
        raise HTTPException(status_code=400, detail="Board or task not found")
    return {"detail": "Task added to board"}


@router.post("/boards/{board_id}/tasks/remove")
def remove_task(board_id: int, data: schemas.TaskToBoard,
                current_user: models.User = Depends(auth.get_current_user),
                db: Session = Depends(database.get_db)):
    # Проверяем, что доска существует
    board = crud.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Проверяем, что задача существует
    task = crud.get_task(db, data.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем, что задача действительно в доске
    if task not in board.tasks:
        raise HTTPException(status_code=400, detail="Task not in board")

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


@router.post("/users/{user_id}/avatar", response_model=schemas.UserOut)
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only update your own avatar")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    file_ext = os.path.splitext(file.filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"user_{user_id}_{timestamp}{file_ext}"

    # Абсолютный путь для сохранения файла
    file_path = os.path.join(AVATAR_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # URL для доступа к аватару (предполагаем, что static/ — статическая папка, монтируется в FastAPI)
    avatar_url = f"/{AVATAR_DIR}/{filename}"

    db_user = crud.update_user_avatar(db, user_id, avatar_url)

    # Удаляем старый аватар, если он есть
    if current_user.avatar_url:
        old_file_path = os.path.join(os.getcwd(), current_user.avatar_url.lstrip('/'))
        if os.path.exists(old_file_path):
            os.remove(old_file_path)

    return db_user


@router.delete("/users/{user_id}/avatar", response_model=schemas.UserOut)
async def delete_avatar(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only delete your own avatar")

    if not current_user.avatar_url:
        raise HTTPException(status_code=400, detail="No avatar to delete")

    # Удаляем файл
    file_path = os.path.join(os.getcwd(), current_user.avatar_url.lstrip('/'))
    if os.path.exists(file_path):
        os.remove(file_path)

    # Обновляем запись в БД
    db_user = crud.update_user_avatar(db, user_id, None)
    return db_user


@router.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user_by_id(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_update: schemas.UserCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    updated_user = crud.update_user(db, user_id, user_update.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=400, detail="Update failed")
    return updated_user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    result = crud.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=400, detail="Delete failed")
    return


@router.get("/users", response_model=list[schemas.UserOut])
def get_all_users(db: Session = Depends(database.get_db)):
    users = crud.get_all_users(db)
    return users


@router.post("/tasks/{task_id}/upload_pdf")
async def upload_pdf(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # Проверяем Content-Type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    content = await file.read()

    # Проверка пустоты файла
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Файл не может быть пустым")

    # Проверка размера
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Размер файла превышает 5 МБ")

    # Формируем путь для сохранения
    file_location = os.path.join(PDF_DIR, f"task_{task_id}.pdf")

    # Сохраняем файл
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Обновляем путь к файлу в задаче
    crud.update_task_pdf(db, task_id, file_location)

    return {"message": "PDF uploaded successfully", "file_path": file_location}


@router.delete("/tasks/{task_id}/delete_pdf")
def delete_pdf(task_id: int, db: Session = Depends(database.get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.pdf_path or not os.path.isfile(task.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    # Удаляем файл из файловой системы
    os.remove(task.pdf_path)

    # Убираем путь из базы
    crud.remove_task_pdf(db, task_id)

    return JSONResponse(content={"message": "PDF deleted successfully"})


@router.put("/tasks/{task_id}/close")
def close_task(task_id: int,
               user_id: int,
               db: Session = Depends(database.get_db)
               ) -> schemas.TaskOut:  # Изменили тип возвращаемого значения
    # Получаем задачу
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Получаем пользователя
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    task.status = "Done"
    task.updated_at = datetime.now()

    user.closed_tasks_count += 1

    db.commit()
    db.refresh(task)

    return schemas.TaskOut.model_validate(task)
