from fastapi import Depends, HTTPException, Query

from fastapi import UploadFile, File, status
from PIL import Image
import io
import os
from typing import Tuple

# Конфигурация
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
AVATAR_SIZE = (400, 400)  # Размер для ресайза


async def validate_image(file: UploadFile) -> Tuple[bytes, str]:
    """Валидация и чтение изображения"""
    # Проверка размера файла
    file.file.seek(0, 2)  # Перемещаемся в конец файла
    file_size = file.file.tell()
    file.file.seek(0)  # Возвращаемся в начало

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Проверка типа файла
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Чтение файла
    try:
        contents = await file.read()
        return contents, file.content_type
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error reading file"
        )


def process_image(image_data: bytes, content_type: str) -> bytes:
    """Ресайз изображения и конвертация в JPEG"""
    try:
        image = Image.open(io.BytesIO(image_data))

        # Конвертация в RGB если нужно (для PNG с альфа-каналом)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')

        # Ресайз с сохранением пропорций
        image.thumbnail(AVATAR_SIZE, Image.LANCZOS)

        # Сохранение в буфер
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        return output.getvalue()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Error processing image"
        )