import json
import requests
from typing import Optional, Dict, Any, Union
from enum import Enum
from helpers.logger import logger


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class BaseService:
    DEFAULT_HEADERS = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    def _make_request(
        self,
        method: HttpMethod,
        url: str,
        body: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Optional[Union[Dict[str, Any], str]]:
        """
        Универсальный метод для выполнения HTTP-запросов

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE, PATCH)
            url: URL для запроса
            body: Тело запроса (для POST, PUT, PATCH)
            params: Query параметры (для GET)
            headers: Заголовки запроса
            **kwargs: Дополнительные параметры для requests

        Returns:
            Ответ в виде словаря/строки или None при ошибке
        """
        final_headers = {**self.DEFAULT_HEADERS, **(headers or {})}

        try:
            if isinstance(body, dict):
                body = json.dumps(body)

            response = requests.request(
                method.value,
                url,
                data=body,
                params=params,
                headers=final_headers,
                **kwargs
            )

            response.raise_for_status()

            # Исправленное логирование
            logger.info(
                "Request successful. Method: %s, URL: %s, Code: %d",
                method.value,
                url,
                response.status_code
            )

            try:
                return response.json()
            except ValueError:
                return response.text

        except requests.exceptions.RequestException as e:
            logger.error(
                "Request failed. Method: %s, URL: %s, Error: %s",
                method.value,
                url,
                str(e)
            )
            return None

    # Методы-алиасы
    def get(self, url: str, **kwargs) -> Optional[Union[Dict[str, Any], str]]:
        return self._make_request(HttpMethod.GET, url, **kwargs)

    def post(self, url: str, body: Optional[Union[Dict[str, Any], str]] = None, **kwargs) -> Optional[
        Union[Dict[str, Any], str]]:
        return self._make_request(HttpMethod.POST, url, body=body, **kwargs)

    def put(self, url: str, body: Optional[Union[Dict[str, Any], str]] = None, **kwargs) -> Optional[
        Union[Dict[str, Any], str]]:
        return self._make_request(HttpMethod.PUT, url, body=body, **kwargs)

    def delete(self, url: str, **kwargs) -> Optional[Union[Dict[str, Any], str]]:
        return self._make_request(HttpMethod.DELETE, url, **kwargs)

    def patch(self, url: str, body: Optional[Union[Dict[str, Any], str]] = None, **kwargs) -> Optional[
        Union[Dict[str, Any], str]]:
        return self._make_request(HttpMethod.PATCH, url, body=body, **kwargs)

    def post_2(self, url, body, token=None):
        try:
            if hasattr(body, 'dict'):
                body = body.model_dump()

            if token:
                self.DEFAULT_HEADERS['Authorization'] = f"Bearer {token}"

            response = requests.post(url, data=json.dumps(body), headers=self.DEFAULT_HEADERS)
            response.raise_for_status()
            logger.info("OK. URL: %s, Code: %d", url, response.status_code)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Error. %s", str(e))
            return None
