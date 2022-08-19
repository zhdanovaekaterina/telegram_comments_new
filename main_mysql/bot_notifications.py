import time as t

import schedule
import telebot

import config
from modules import functions as f

bot = telebot.TeleBot(config.bot_token)
bot.delete_webhook()


def send_new_comments():
    def send_comments():
        flag, list_of_users, notification_message, list_of_buttons = f.prepare_comments()
        if flag:
            for user in list_of_users:
                bot.send_message(user, notification_message, reply_markup=list_of_buttons)
    schedule.every(30).minutes.do(send_comments)

    while True:
        schedule.run_pending()
        t.sleep(5)


if __name__ == '__main__':
    pass
