from weather_api_connector import WeatherAPIConnector
from transformer import WeatherTransformer
from shared.utils import Moment

# Connecting weather API
weather_connector = WeatherAPIConnector("http://api.weatherapi.com/v1")
# Connecting transformer
weather_transformer = WeatherTransformer(weather_connector)
# Returning weather report
print(weather_transformer.transform(weather_connector.get_forecast('Grimbergen'), Moment.FULL))
