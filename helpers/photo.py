from PIL import Image, ImageDraw
import os


def create_test_photo():
    # Создаем изображение 800x800 пикселей
    img = Image.new('RGB', (800, 800), color='white')
    draw = ImageDraw.Draw(img)

    # Рисуем силуэт человека
    # Голова
    draw.ellipse((300, 100, 500, 300), fill='black')

    # Тело
    draw.rectangle((375, 300, 425, 500), fill='black')

    # Руки
    draw.line((375, 350, 275, 400), fill='black', width=25)
    draw.line((425, 350, 525, 400), fill='black', width=25)

    # Ноги
    draw.line((375, 500, 375, 650), fill='black', width=25)
    draw.line((425, 500, 425, 650), fill='black', width=25)

    # Сохраняем изображение
    if not os.path.exists('user_photos'):
        os.makedirs('user_photos')

    img.save('user_photos/test_photo.jpg', 'JPEG', quality=85)

    # Проверяем размер файла
    file_size = os.path.getsize('user_photos/test_photo.jpg') / (1024 * 1024)  # в MB
    print(f"Test photo created. Size: {file_size:.2f} MB")


if __name__ == '__main__':
    create_test_photo()