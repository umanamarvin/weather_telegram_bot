import logging
import os
import asyncio
import shared.constants

from telegram.ext import Application
from weather_api.transformer import WeatherTransformer
from weather_api.weather_api_connector import WeatherAPIConnector
from shared.utils import Moment
from database.database import DatabaseConnector

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.INFO)

logger = logging.getLogger(__name__)


class AutomaticReports:
    def __init__(self, application: Application, url: str):
        self.connector = WeatherAPIConnector(url=url)
        self.transformer = WeatherTransformer(connector=self.connector)
        self.application = application

    async def send_reports(self) -> None:
        """Sends weather reports to users who have agreed to receive automated updates."""
        db_connector = DatabaseConnector(
            db_name=shared.constants.DB_NAME,
            user=shared.constants.DB_USER,
            password=shared.constants.DB_PASSWORD,
            host=shared.constants.HOST,
            port=shared.constants.PORT,
        )

        users = db_connector.read_users(agreement=True, subscription=True, active=True)

        for user in users:
            weather_update = self.transformer.transform(user.latitude, user.longitude, Moment.FORECAST)

            try:
                await self.application.bot.send_message(
                    chat_id=user.chat_id,
                    text=f"{weather_update}"
                )
                logger.info(f"Sent weather update to user {user.chat_id}")
            except Exception as e:
                logger.error(f"Failed to send weather update to user {user.chat_id}: {e}")


def main() -> None:
    """Run the automatic reports sender."""
    tel_token = os.environ.get("TEL_API_KEY", None)
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(tel_token).build()

    automatic_reports = AutomaticReports(application, 'http://api.weatherapi.com/v1')

    # Send weather reports immediately when the script runs
    asyncio.run(automatic_reports.send_reports())

if __name__ == "__main__":
    main()
    