#!/usr/bin/env python
# pylint: disable=unused-argument, import-error
# This program is dedicated to the public domain under the CC0 license.

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, CallbackContext
from telegram.ext.filters import LOCATION

from shared.models import UserData
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


class TelegramBot:
    def __init__(self, application: Application, url: str):
        self.connector = WeatherAPIConnector(url=url)
        self.transformer = WeatherTransformer(connector=self.connector)

        self.application = application
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CallbackQueryHandler(self.button))
        self.application.add_handler(MessageHandler(LOCATION, self.handle_location))
        self.application.add_handler(CommandHandler('help', self.help_command))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends a message with three inline buttons attached."""
        keyboard = [
            [InlineKeyboardButton("Get current weather conditions", callback_data="current")],
            [InlineKeyboardButton("Subscribe foe automated daily weather updates", callback_data="automation")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Welcome to your personal weather forecast assistant, what do you want to do:",
            reply_markup=reply_markup
        )

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        callback_data = update.callback_query
        logger.warning(f"Received message: {update.to_dict()}")
        await callback_data.answer()
        if callback_data.data == 'current':
            reply_markup = self.create_location_sharing_button()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please share your location, using the command button.",
                reply_markup=reply_markup
            )
            context.user_data['last_button'] = 'current'
        elif callback_data.data == 'automation':
            context.user_data['last_button'] = 'automation'
            await self.consent_confirmation_button(update, context)
        elif callback_data.data == 'confirm':
            reply_markup = self.create_location_sharing_button()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please share your location, using the command button.",
                reply_markup=reply_markup
            )
        elif callback_data.data == 'decline':
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="We can't deliver automatic updates, if we can't store your location and chat information. Please use the /start command to get current weather conditions or accept the consent."
            )

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Displays info on how to use the bot."""
        await update.message.reply_text("Use /start to test this bot.")

    async def handle_location(self, update: Update, context: CallbackContext) -> None:
        user_location = update.message.location
        logger.warning(f"Location of the user is: {user_location}")
        if not context.user_data or context.user_data['last_button'] == 'current':
            await update.message.reply_text(
                text='Sending current weather conditions. If you want to subscribe for automated updates, send the command /start and select the button subscribe to automated updates.'
            )
            weather_update = self.transformer.transform(user_location.latitude, user_location.longitude, Moment.CURRENT)
            await update.message.reply_text(
                text=f"{weather_update}"
            )
        elif context.user_data['last_button'] == 'automation':
            user_data_to_save = UserData(
                chat_id=update.effective_chat.id,
                latitude=user_location.latitude,
                longitude=user_location.longitude,
                agreement=True,
                subscription=True,
                active=True
            )
            self.insert_user_data_into_db(user_data_to_save)
            await update.message.reply_text(
                text='You location will be saved in order to send you automated weather updates.'
            )

    async def consent_confirmation_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
            [InlineKeyboardButton("Confirm Consent", callback_data="confirm")],
            [InlineKeyboardButton("Decline Consent", callback_data="decline")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_message.reply_text(
            "To subscribe, you need to accept that we store your location and chat data.",
            reply_markup=reply_markup
        )

    @staticmethod
    def create_location_sharing_button():
        button_location = KeyboardButton(text="Share location", request_location=True)
        custom_keyboard = [[button_location]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)
        return reply_markup

    @staticmethod
    def insert_user_data_into_db(user_data: UserData):
        db_conn = DatabaseConnector(
            db_name=os.environ.get('DB_NAME', None),
            user=os.environ.get('DB_USER', None),
            password=os.environ.get('DB_PASSWORD', None),
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432'),
        )
        db_conn.insert_user(user_data)
        db_conn._commit_and_close()


def main() -> None:
    """Run the bot."""
    tel_token = os.environ.get("TEL_API_KEY", None)
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(tel_token).build()

    bot = TelegramBot(application, 'http://api.weatherapi.com/v1')

    # Run the bot until the user presses Ctrl-C
    bot.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
