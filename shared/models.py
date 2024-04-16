from pydantic import BaseModel


class UserData(BaseModel):
    """
    DataClass got from Spanner (Important data for scripts)
    """
    # id: str
    chat_id: str | int
    latitude: float | None = None
    longitude: float | None = None
    agreement: bool = False
    subscription: bool = False
    active: bool = True

    def get_query_string(self):
        return '''
        INSERT INTO users (chat_id, latitude, longitude, agreement, subscription, active)
        VALUES ({}, {}, {}, {}, {}, {})
        '''.format(
            self.chat_id, self.latitude, self.longitude, self.agreement, self.subscription, self.active
        )

    @classmethod
    def from_database(cls, db_data):
        """
        Create a UserData instance from database data.
        """
        return cls(
            chat_id=db_data[1],
            latitude=db_data[2],
            longitude=db_data[3],
            agreement=db_data[4],
            subscription=db_data[5],
            active=db_data[6],
        )


# chat_id = db_data['chat_id'],
# latitude = db_data['latitude'],
# longitude = db_data['longitude'],
# agreement = db_data['agreement'],
# subscription = db_data['subscription'],
# active = db_data['active'],


# ----------- Weather API Models -----------

class WeatherForecastDayAstro(BaseModel):
    sunrise: str
    sunset: str


class WeatherForecastDayCondition(BaseModel):
    text: str


class WeatherForecastDay(BaseModel):
    condition: WeatherForecastDayCondition
    maxtemp_c: float
    mintemp_c: float


class WeatherForecastItem(BaseModel):
    astro: WeatherForecastDayAstro
    day: WeatherForecastDay


class WeatherForecast(BaseModel):
    forecastday: list[WeatherForecastItem]


class CurrentWeatherCondition(BaseModel):
    text: str


class CurrentWeather(BaseModel):
    temp_c: float
    condition: CurrentWeatherCondition
    feelslike_c: float


class WeatherLocation(BaseModel):
    name: str
    tz_id: str


class WeatherReport(BaseModel):
    """
    DataClass representation of the WeatherAPI response
    """
    location: WeatherLocation
    current: CurrentWeather
    forecast: WeatherForecast


# ----------- Telegram Models -----------


class ChatResponse(BaseModel):
    """
    DataClass representation of the Telegram Bot response, parsed into what we need and want as most important data
    """
    pass


class ChatMessage(BaseModel):
    """
    DataClass representation of the message which will be sent to a certain Telegram Chat
    """
    pass
