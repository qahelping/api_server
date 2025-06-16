# import Faker
import pytest
from faker import Faker

from app import schemas
from helpers.app_service import AppService


@pytest.fixture
def service():
    return AppService()

@pytest.fixture
def login_with_new_user(service: AppService):
    user = schemas.UserCreate(username=Faker().user_name(), password="testpass1")
    service.create_user(user)
    service.token = service.login(user).get('access_token')

@pytest.fixture
def login(app_service: AppService):
    service = AppService()
    # fake = Faker()
    user = schemas.UserCreate(username=f'name', password="password")
    service.create_user(user)
    response = service.login(user)
    return response.access_token