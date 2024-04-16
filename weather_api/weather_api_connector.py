import http
import os
from shared.connector import APIConnector


class WeatherAPIConnector(APIConnector):
    CREDENTIALS: dict = None

    def _get_auth_data(self):
        """
        Function used to get the authentication data

        Must override function when inheriting from this class
        :return:
        """
        return os.environ.get("API_KEY", None)

    def get_forecast(self, location: str) -> dict:
        wea_token = self._get_auth_data()
        params = {'key':  wea_token, 'q': location, 'days': 2}
        return self.perform_request(http.HTTPMethod.GET, 'forecast.json', params=params)
