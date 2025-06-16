import json
import requests
from typing import Optional, Dict, Any, Union
from enum import Enum, auto

from app import schemas
from helpers.base_services import BaseService
from helpers.logger import logger


class AppService(BaseService):
    BASE_URL = "http://127.0.0.1:8001"
    token = ''

    def create_user(self, user: schemas.UserCreate):
        url = f"{self.BASE_URL}/users/register"
        return schemas.UserOut(**self.post_2(url, user))

    def login(self, user: schemas.UserCreate):
        url = f"{self.BASE_URL}/login"
        return self.post_2(url, user)


    def create_task(self, task: schemas.TaskCreate):
        url = f"{self.BASE_URL}/tasks"
        return schemas.TaskOut(**self.post_2(url, task, self.token))
