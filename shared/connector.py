import abc
import http
import json
from typing import Optional
import os
import requests


class APIConnector(abc.ABC):
    CREDENTIALS: dict = None

    def __init__(self, url: str):
        self.url = url

    @abc.abstractmethod
    def _get_auth_data(self):
        """
        Function used to get the authentication data

        Must override function when inheriting from this class
        :return:
        """
        raise NotImplementedError()

    def perform_request(self, method: http.HTTPMethod, endpoint: str, body: Optional[dict] = None, params: Optional[dict] = None):
        """
        Function to perform an API request

        Can be overriden when inheriting from this class.

        Do note, each API might have slight differences, therefore, check if the current functionality is good enough
        or make the changes you need for your use case.

        NOTE: The current implementation does not take into account authentication.

        Also if you override the function, please make sure you handle error responses correctly.

        :param method: The HTTP method the request will have (POST, GET, PUT, etc)
        :param endpoint: The endpoint you need to reach within the API
        :param body: The request's body (Optional param)
        :param params: The request's header params (Optional param)
        :return: Returns the response object's json.
        """
        headers = {}
        if body:
            headers['Content-type'] = 'application/json'

        response = requests.request(
            method=method,
            headers=headers,
            url=f'{self.url}/{endpoint}',
            data=json.dumps(body),
            params=params
        )

        if response.status_code != http.HTTPStatus.OK:
            raise ValueError(f'Received other status code than 200. [Status Code: {response.status_code} - Message:{response.text}]')

        if response.status_code >= 500:
            raise ConnectionError('Received 500 Error, check if app is down.')
        elif response.status_code >= 400:
            raise ValueError('Received 400 Error, check data to confirm its correct.')
        else:
            return response.json()
