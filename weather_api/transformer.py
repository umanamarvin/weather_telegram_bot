from typing import Type, TypeVar, Optional

from shared.models import WeatherReport
from shared.transformer import BaseTransformer
from shared.utils import Moment
# This should be a dataclass per transformer to define how the transformed data should look like.
TransformerModel = TypeVar('TransformerModel')


class WeatherTransformer(BaseTransformer):

    def transform(self, latitude: float, longitude: float, moment: Moment | None = None) -> str:
        """
        base function to transform the data received by the connector class.

        :return: transformed data into desired form -> child object of the class TransformerModel
        """
        report: WeatherReport = self.get_data(latitude, longitude, moment)

        # Processing and format to the data to a readable form
        tomorrow_forecast = report.forecast.forecastday[1]
        today_weather = report.current
        location = report.location.name
        if moment == Moment.CURRENT:
            return f'{today_weather.condition.text} at the moment in {location}\nWith a temperature of {today_weather.temp_c}°c\nAnd it feels like {today_weather.feelslike_c}°c'
        elif moment == Moment.FORECAST:
            return f'{tomorrow_forecast.day.condition.text} for tomorrow in {location}\nWith a Max temperature of {tomorrow_forecast.day.maxtemp_c}°c and Min of {tomorrow_forecast.day.mintemp_c}°c\nSunrise at {tomorrow_forecast.astro.sunrise} and Sunset at {tomorrow_forecast.astro.sunset}'
        elif moment == Moment.FULL:
            return f'{today_weather.condition.text} at the moment in {location}\nWith a temperature of {today_weather.temp_c}°c\nAnd it feels like {today_weather.feelslike_c}°c\n\n{tomorrow_forecast.day.condition.text} for tomorrow in {location}\nWith a Max temperature of {tomorrow_forecast.day.maxtemp_c}°c and Min of {tomorrow_forecast.day.mintemp_c}°c\nSunrise at {tomorrow_forecast.astro.sunrise} and Sunset at {tomorrow_forecast.astro.sunset}'
        else:
            raise ValueError('Error detail: Input moment for report')

    def get_data(self, latitude: float, longitude: float, moment: str | None = None) -> WeatherReport:
        """
        Function to get the needed data form the API in order to receive the response.

        Must be implemented by child classes.
        :return: dict
        """
        data = self.connector.get_forecast(f'{latitude},{longitude}')

        # Convert the data to a Pydantic model
        report = WeatherReport(**data)

        return report
