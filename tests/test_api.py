import pytest
from faker import Faker

from app import schemas
from app.schemas import UserOut
from helpers.app_service import AppService

BASE_URL = "http://127.0.0.1:8001"


# def test_create_user():
#     service = AppService()
#     user = schemas.UserCreate(username=Faker().user_name(), password="testpass1")
#     user_out: UserOut = service.create_user(user)
#     assert user_out.id > 0
#     assert user_out.username == user.username
#     assert user_out.avatar_url is None
#
# def test_login():
#     service = AppService()
#     user = schemas.UserCreate(username=Faker().user_name(), password="testpass1")
#     service.create_user(user)
#
#     assert service.login(user).get('access_token')

@pytest.fixture
def service():
    return AppService()

@pytest.fixture
def login_with_new_user(service: AppService):
    user = schemas.UserCreate(username=Faker().user_name(), password="testpass1")
    service.create_user(user)
    service.token = service.login(user).get('access_token')


def test_create_task(service, login_with_new_user):
    fake = Faker()
    task = schemas.TaskCreate(title=fake.user_name(), description=fake.last_name(), priority='Low', status='Open')
    print(service.token)
    response = service.create_task(task)
    print(response)

