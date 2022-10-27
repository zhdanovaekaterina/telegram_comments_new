from telebot import types

import src.config as config
from modules import functions as f, messages


class Buttons:
    def __init__(self):
        self.buttons = types.InlineKeyboardMarkup()

    @staticmethod
    def _url_button(text, url):
        return types.InlineKeyboardButton(text=text, url=url)

    @staticmethod
    def _callback_button(text, callback_data):
        return types.InlineKeyboardButton(text=text, callback_data=callback_data)

    @property
    def start_command_button(self):
        button = self._url_button(messages.documentation, config.documentation_url)
        self.buttons.add(button)
        return self.buttons
