# This Python file uses the following encoding: ascii
# This module describes the work of Telegram bot interface.
# The goal is to make the work with comments tracking avaliable for marketer.

import telebot
from telebot import types
import config
import messages
import re
import sqlite3 as sl
from test_post_object import TestObject
from functions import generate_buttons_list
from objects import NewPost
import bot_functions.bot_add_post_procedure


bot = telebot.TeleBot(config.bot_token)
bot.delete_webhook()


# <-- Command handlers section -->


@bot.message_handler(commands=['start'])  # Ready
def start_command(message):
    """Sends greeting message and the list of commands available."""
    bot.send_message(message.chat.id, messages.start_message)


@bot.message_handler(commands=['add'])  # Partly ready (look to-do)
def add_command(message):
    """Adds a new post to tracking."""
    list_of_buttons = generate_buttons_list('post_add')
    add_button = types.InlineKeyboardButton(text=messages.add_client_button,
                                            callback_data='add_new_client')
    list_of_buttons.add(add_button)  # Adds a button to add new client
    bot.send_message(message.chat.id, messages.add_message, reply_markup=list_of_buttons)
    # TODO: add the processing of user input text


@bot.message_handler(commands=['clients'])  # Partly ready (look to-do)
def clients_command(message):
    """Sends the list of added clients. Gives a chance to select client."""
    list_of_buttons = generate_buttons_list('select_active_client')
    add_button = types.InlineKeyboardButton(text=messages.add_client_button,
                                            callback_data='add_new_client')
    list_of_buttons.add(add_button)  # Adds a button to add new client
    bot.send_message(message.chat.id, messages.client_list_message, reply_markup=list_of_buttons)
    # TODO: add the processing of user input text


@bot.message_handler(commands=['help'])  # Ready
def help_command(message):
    """Sends the list of available commands and their descriptions."""
    bot.send_message(message.chat.id, messages.help_message)


@bot.message_handler(commands=['archive'])  # Ready
def archive_command(message):
    """Sends the list clients who have at least 1 archived post."""
    list_of_buttons = generate_buttons_list('select_archive_client')
    bot.send_message(message.chat.id, messages.client_archive_message, reply_markup=list_of_buttons)


# <-- Callback handlers section -->


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^post_add_.*', call.data))
def select_client_query(call):
    """Starts the procedure of adding new post to tracking.
    Saves client_id to the NewPost object.
    Step 1: Ask to input post name.
    """
    bot.answer_callback_query(call.id)
    client_id = call.data.split('_')[-1]
    new_post = NewPost()
    new_post.add_client_id(client_id)
    msg = bot.send_message(call.from_user.id, messages.ask_post_name)
    bot.register_next_step_handler(msg, process_post_link_input(new_post))


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^select_active_client_.*', call.data))
def select_client_query(call):
    """Sends the short information about client and a list of its posts."""
    bot.answer_callback_query(call.id)
    client_name = call.data.split('_')[-1]
    list_of_buttons = generate_buttons_list('select_active_post', client_name)
    bot.send_message(call.from_user.id, messages.post_list_message, reply_markup=list_of_buttons)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^select_active_post_.*', call.data))
def select_client_query(call):
    """Sends the short information about a post and a few options:
    - see all comments;
    - go to the original post;
    - disable tracking.
    """
    bot.answer_callback_query(call.id)
    # TODO: add the connection to db to take the information about the post and send it to the user.
    # TODO: add some user options (listed in docstring).


@bot.callback_query_handler(func=lambda call: call.data == 'add_new_client')
def add_client_query(call):
    """Adds new client to the base. In the end propose to add a new post for tracking for this client."""
    bot.answer_callback_query(call.id)
    pass


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^select_archive_client_.*', call.data))
def select_client_query(call):
    """Sends the short information about client and a list of its posts with short stats."""
    bot.answer_callback_query(call.id)
    pass


# <-- Message handlers section -->


@bot.message_handler(content_types=['text'])
def process_post_link_input(message, new_post):
    """Continues the procedure of adding new post to tracking.
    Saves post name to the NewPost object.
    Step 2: Ask to input post link.
    """
    post_name = message.text
    new_post.add_post_name(post_name)
    msg = bot.send_message(message.chat.id, messages.ask_post_link)
    bot.register_next_step_handler(msg, finish_post_add(new_post))


@bot.message_handler(content_types=['text'])
def finish_post_add(message, new_post):
    """Finishes the procedure of adding new post to tracking.
    Checks if message is a correct Telegram link.
    Parse user's link and save channel_name and channel_post_id to the NewPost object.
    Add attributes of NewPost object to db.
    Step 3: Finish the procedure.
    """
    if re.fullmatch(r'^https://t\.me/.+/.+$', message.text):
        new_post.add_channel_name(message.text.split('/')[-2])
        new_post.add_channel_post_id(message.text.split('/')[-1])
        # TODO: add the connection to db to add the new post.
        new_post.default_condition()
        bot.send_message(message.chat.id, messages.success_add_post)
    else:
        msg = bot.send_message(message.chat.id, messages.ask_post_link_second_time)
        bot.register_next_step_handler(msg, finish_post_add(new_post))


bot.polling()
