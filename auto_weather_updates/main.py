from telegram import Bot

from google_connector.sm import LazySecret
from shared.utils import Moment
from weather_api.transformer import WeatherTransformer
from weather_api.weather_api_connector import WeatherAPIConnector


def main():
    # Prepare the bot and transformer
    lazystring = LazySecret('')
    tel_token = lazystring.get_secret('telegram-api-secret', 1)
    bot = Bot(token=tel_token)

    connector = WeatherAPIConnector(url='http://api.weatherapi.com/v1')
    transformer = WeatherTransformer(connector=connector)

    # TODO: get data from db to perform the auto updates
    #  mainly chat_id is important here. Gather a list of all chat_ids to send the update to. Also the coordinates are crucial.
    chat_ids: list = []
    # Concatenate the latitude + the longitude and formatted correctly
    coordinates = ""
    for chat_id in chat_ids:
        message = transformer.transform(coordinates=coordinates, moment=Moment.FORECAST)
        bot.send_message(chat_id=chat_id, text=message)
    return


if __name__ == "__main__":
    main()
