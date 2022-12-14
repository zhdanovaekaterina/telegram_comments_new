# This Python file uses the following encoding: ascii
# This module describes the work of Telegram bot interface.
# The goal is to make the work with comments tracking avaliable for marketer.

import re
import logging

import telebot
from telebot import types

import src.config as config
from modules import functions as f, messages
from classes.buttons import Buttons
from src.decorators import connectionerror

# Configure bot
bot = telebot.TeleBot(config.bot_token)
bot.delete_webhook()

# Global variables declaration
post_id = None
client_id = None
post_name = None

# Logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
                    force=True,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )


# <-- Notifications section -->


@bot.message_handler(func=lambda message: message.chat.id not in f.list_of_user_ids())
def check_user_id(message):
    print(message.chat.id)
    bot.send_message(message.chat.id, messages.no_permission)
    your_user_id = f.your_user_id(message.chat.id)
    bot.send_message(message.chat.id, your_user_id)


# <-- Command handlers section -->


@bot.message_handler(commands=['start'])
def start_command(message):
    print(message.chat.id)
    bot.send_message(message.chat.id, messages.start_message, reply_markup=Buttons().start_command_button)


@bot.message_handler(commands=['add'])
def add_command(message):
    """Adds a new post to tracking."""
    list_of_buttons = f.generate_buttons_list('post_add')
    if list_of_buttons is not None:
        add_button = types.InlineKeyboardButton(text=messages.add_client_button,
                                                callback_data='add_new_client')
        list_of_buttons.add(add_button)  # Adds a button to add new client
        bot.send_message(message.chat.id, messages.add_message, reply_markup=list_of_buttons)
    else:
        list_of_buttons = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton(text=messages.client_button,
                                                callback_data=f'add_new_client')
        no_button = types.InlineKeyboardButton(text=messages.nothing,
                                               callback_data='exit')
        list_of_buttons.add(yes_button, no_button)
        bot.send_message(message.chat.id, messages.empty_client_list_when_add, reply_markup=list_of_buttons)


@bot.message_handler(commands=['clients'])
def clients_command(message):
    """Sends the list of added clients. Gives a chance to select client."""
    list_of_buttons = f.generate_buttons_list('select_active_client')
    if list_of_buttons is not None:
        add_button = types.InlineKeyboardButton(text=messages.add_client_button,
                                                callback_data='add_new_client')
        list_of_buttons.add(add_button)  # Adds a button to add new client
        bot.send_message(message.chat.id, messages.client_list_message, reply_markup=list_of_buttons)
    else:
        list_of_buttons = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton(text=messages.client_button,
                                                callback_data=f'add_new_client')
        no_button = types.InlineKeyboardButton(text=messages.nothing,
                                               callback_data='exit')
        list_of_buttons.add(yes_button, no_button)
        bot.send_message(message.chat.id, messages.empty_client_list, reply_markup=list_of_buttons)


@bot.message_handler(commands=['help'])
def help_command(message):
    """Sends the list of available commands and their descriptions."""
    buttons = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text=messages.documentation,
                                        url=config.documentation_url)
    buttons.add(button)
    bot.send_message(message.chat.id, messages.help_message, reply_markup=buttons)


@bot.message_handler(commands=['archive'])
def archive_command(message):
    """Sends the list clients who have at least 1 archived post."""
    list_of_buttons = f.generate_buttons_list('select_archive_client')
    if list_of_buttons is not None:
        bot.send_message(message.chat.id, messages.client_archive_message, reply_markup=list_of_buttons)
    else:
        bot.send_message(message.chat.id, messages.empty_archive)


@bot.message_handler(commands=['updates'])
def updates_command(message):
    """Sends the list of new comments."""
    result = f.prepare_comments()
    if result.flag:
        bot.send_message(message.chat.id, result.notification_message, reply_markup=result.list_of_buttons)
    else:
        bot.send_message(message.chat.id, messages.no_updates)


@bot.message_handler(commands=['crash'])
def updates_command(message):
    """Deletes all users from white list."""
    f.delete_all_users()
    bot.send_message(message.chat.id, messages.no_users)


# <-- Callback handlers section -->


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^post_add_.*', call.data))
def post_add_1(call):
    """Starts the procedure of adding new post to tracking.
    Step 1: Ask to input post name.
    """
    bot.answer_callback_query(call.id)
    global client_id
    client_id = call.data.split('_')[-1]

    msg = bot.send_message(call.from_user.id, messages.ask_post_name)
    bot.register_next_step_handler(msg, process_post_link_input)


@bot.callback_query_handler(func=lambda call: call.data == 'add_post')
def add_another_post_command(call):
    """Adds a new post to tracking."""
    bot.answer_callback_query(call.id)
    list_of_buttons = f.generate_buttons_list('post_add')
    add_button = types.InlineKeyboardButton(text=messages.add_client_button,
                                            callback_data='add_new_client')
    list_of_buttons.add(add_button)  # Adds a button to add new client
    bot.send_message(call.from_user.id, messages.add_message, reply_markup=list_of_buttons)
    # TODO: add the processing of user input text


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^select_active_client_.*', call.data))
def select_active_client(call):
    """Sends the short information about client and a list of its posts."""
    bot.answer_callback_query(call.id)
    client_id = call.data.split('_')[-1]
    list_of_buttons = f.generate_buttons_list('select_active_post', client_id)
    if list_of_buttons is not None:
        archive_client_button = types.InlineKeyboardButton(text=messages.archive_client,
                                                           callback_data=f'archive_client_1_{client_id}')
        list_of_buttons.add(archive_client_button)
        bot.send_message(call.from_user.id, messages.post_list_message, reply_markup=list_of_buttons)
    else:
        list_of_buttons = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton(text=messages.add_button,
                                                callback_data=f'post_add_{client_id}')
        no_button = types.InlineKeyboardButton(text=messages.nothing,
                                               callback_data='exit')
        list_of_buttons.add(yes_button, no_button)
        bot.send_message(call.from_user.id, messages.empty_post_list, reply_markup=list_of_buttons)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^select_active_post_.*', call.data))
def select_active_post(call):
    """Sends the short information about a post and a few options:
    - see all comments;
    - go to the original post;
    - disable tracking.
    """
    bot.answer_callback_query(call.id)
    post_id = call.data.split('_')[-1]
    post_info = f.get_post_details(post_id)

    if post_info[1] is not None:
        list_of_buttons = types.InlineKeyboardMarkup(row_width=2)
        watch_comments_button = types.InlineKeyboardButton(text=messages.watch_comments,
                                                           callback_data=f'give_comments_list_0_{post_id}')
        go_to_post_button = types.InlineKeyboardButton(text=messages.go_to_post,
                                                       url=post_info[1])
        archive_post_button = types.InlineKeyboardButton(text=messages.archive_post,
                                                         callback_data=f'archive_post_{post_id}')
        list_of_buttons.add(watch_comments_button, go_to_post_button, archive_post_button)
        bot.send_message(call.from_user.id, post_info[0], reply_markup=list_of_buttons)

    else:
        bot.send_message(call.from_user.id, post_info[0])


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^give_comments_list_.*', call.data))
def give_comments_list(call):
    """Sends the list of comments under the selected post."""
    bot.answer_callback_query(call.id)
    post_id = call.data.split('_')[-1]
    need_only_new = True if int(call.data.split('_')[-2]) == 1 else False

    comments_info = f.comment_info(post_id, need_only_new)
    if need_only_new == 1:
        f.delete_is_new_flags(post_id)
    if comments_info is not None:
        list_of_buttons = types.InlineKeyboardMarkup()
        go_to_post_button = types.InlineKeyboardButton(text=messages.go_to_post,
                                                       url=comments_info[1])
        list_of_buttons.add(go_to_post_button)
        bot.send_message(call.from_user.id, comments_info[0], reply_markup=list_of_buttons)
    else:
        bot.send_message(call.from_user.id, messages.no_comments_yet)


@bot.callback_query_handler(func=lambda call: call.data == 'add_new_client')
def add_new_client(call):
    """Starts the procedure of adding new client to the base.
    Step 1: ask for client name.
    """
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.from_user.id, messages.ask_client_name)
    bot.register_next_step_handler(msg, process_new_client)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^select_archive_client_.*', call.data))
def select_archive_client(call):
    """Sends the short information about client and a list of its posts with short stats."""
    bot.answer_callback_query(call.id)
    client_id = call.data.split('_')[-1]
    list_of_buttons = f.generate_buttons_list('select_archive_post', client_id)
    bot.send_message(call.from_user.id, messages.client_posts_archive_message, reply_markup=list_of_buttons)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^return_client_.*', call.data))
def return_client_to_active(call):
    """Returns client into active state. All posts of the client in this case are still archived."""
    bot.answer_callback_query(call.id)
    client_id = call.data.split('_')[-1]

    f.return_client(client_id)

    list_of_buttons = types.InlineKeyboardMarkup()
    add_post_button = types.InlineKeyboardButton(text=messages.add_post,
                                                 callback_data=f'post_add_{client_id}')
    nothing_button = types.InlineKeyboardButton(text=messages.nothing,
                                                callback_data='exit')
    list_of_buttons.add(add_post_button, nothing_button)
    bot.send_message(call.from_user.id, messages.success_return_client, reply_markup=list_of_buttons)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^select_archive_post_.*', call.data))
def select_archive_post(call):
    """Sends short information about selected post and propose to return it to tracking or delete."""
    bot.answer_callback_query(call.id)
    post_id = call.data.split('_')[-1]
    post_info = f.get_post_details(post_id)
    list_of_buttons = types.InlineKeyboardMarkup()
    track_again_button = types.InlineKeyboardButton(text=messages.track_again,
                                                    callback_data=f'track_again_{post_id}')
    delete_button = types.InlineKeyboardButton(text=messages.delete_post,
                                               callback_data=f'delete_post_1_{post_id}')
    list_of_buttons.add(track_again_button, delete_button)
    bot.send_message(call.from_user.id, post_info[0], reply_markup=list_of_buttons)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^track_again_.*', call.data))
def track_again(call):
    """Returns archived post to tracking."""
    bot.answer_callback_query(call.id)
    post_id = call.data.split('_')[-1]
    f.track_status(post_id)
    bot.send_message(call.from_user.id, messages.success_add_post)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^delete_post_1_.*', call.data))
def delete_post_1(call):
    """Deletes post from statistics. Asks for password for this action."""
    bot.answer_callback_query(call.id)
    global post_id
    post_id = call.data.split('_')[-1]
    msg = bot.send_message(call.from_user.id, messages.ask_password)
    bot.register_next_step_handler(msg, delete_post)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^archive_client_1_.*', call.data))
def archive_client_1(call):
    """Starts the move-to-archive procedure.
    Step 1: verification.
    """
    bot.answer_callback_query(call.id)
    client_id = call.data.split('_')[-1]
    list_of_buttons = types.InlineKeyboardMarkup()
    archive_button = types.InlineKeyboardButton(text=messages.archive_client,
                                                callback_data=f'archive_client_2_{client_id}')
    list_of_buttons.add(archive_button)
    bot.send_message(call.from_user.id, messages.archive_client_verification, reply_markup=list_of_buttons)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^archive_client_2_.*', call.data))
def archive_client_2(call):
    """Finishes the move-to-archive procedure.
    Step 2: moves client and all its posts to archive.
    """
    bot.answer_callback_query(call.id)
    client_id = call.data.split('_')[-1]
    f.archive_client(client_id)
    bot.send_message(call.from_user.id, messages.success_archive_client)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^archive_post_.*', call.data))
def archive_post(call):
    """Starts the move-to-archive procedure."""
    bot.answer_callback_query(call.id)
    post_id = call.data.split('_')[-1]
    f.track_status(post_id, to_archive=True)
    bot.send_message(call.from_user.id, messages.success_archive_post)


@bot.callback_query_handler(func=lambda call: call.data == 'exit')
def exit_function(call):
    """Finishes the procedure of adding new client."""
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, messages.nothing_message)


# <-- Message handlers section -->


@bot.message_handler(content_types=['text'])
def process_post_link_input(message):
    """Continues the procedure of adding new post to tracking.
    Saves post name to temporary csv file.
    Step 2: Ask to input post link.
    """
    if message.text == 'STOP':
        bot.send_message(message.chat.id, messages.stop_message)
        return

    global post_name
    post_name = message.text

    msg = bot.send_message(message.chat.id, messages.ask_post_link)
    bot.register_next_step_handler(msg, finish_post_add)


@bot.message_handler(content_types=['text'])
def finish_post_add(message):
    """Finishes the procedure of adding new post to tracking.
    Checks if message is a correct Telegram link.
    Parse user's link and save channel_name and channel_post_id to the NewPost object.
    Add attributes of NewPost object to db.
    Step 3: Finish the procedure.
    """
    if message.text == 'STOP':
        bot.send_message(message.chat.id, messages.stop_message)
        return

    if re.fullmatch(r'^https://t\.me/.+/.+$', message.text):
        global client_id, post_name
        channel_name = message.text.split('/')[-2]
        channel_post_id = message.text.split('/')[-1]

        is_in_base = f.check_post(channel_name, channel_post_id)
        if not is_in_base[0]:
            f.add_post(client_id, post_name, channel_name, channel_post_id)
            client_id, post_name = None, None
            bot.send_message(message.chat.id, messages.success_add_post_first_time)
        else:
            client_id, post_name = None, None
            list_of_buttons = types.InlineKeyboardMarkup()
            yes_button = types.InlineKeyboardButton(text=messages.add_another_post,
                                                    callback_data='add_post')
            no_button = types.InlineKeyboardButton(text=messages.nothing,
                                                   callback_data='exit')
            list_of_buttons.add(yes_button, no_button)
            bot.send_message(message.chat.id, messages.post_already_exists, reply_markup=list_of_buttons)

    else:
        msg = bot.send_message(message.chat.id, messages.ask_post_link_second_time)
        bot.register_next_step_handler(msg, finish_post_add)


@bot.message_handler(content_types=['text'])
def process_new_client(message):
    """Finishes the procedure of adding new client.
    Step 2: Check user's input and add client to the base.
    """
    if message.text == 'STOP':
        bot.send_message(message.chat.id, messages.stop_message)
        return

    client_name = message.text

    # Check if client is already in base
    in_base = f.check_client(client_name)

    # Add new client and propose to add a post for this client
    if not in_base[0]:
        client_added = f.add_client(client_name)

        list_of_buttons = types.InlineKeyboardMarkup()
        add_post_button = types.InlineKeyboardButton(text=messages.add_post,
                                                     callback_data=f'post_add_{client_added}')
        nothing_button = types.InlineKeyboardButton(text=messages.nothing,
                                                    callback_data='exit')
        list_of_buttons.add(add_post_button, nothing_button)
        bot.send_message(message.chat.id, messages.success_add_client, reply_markup=list_of_buttons)

    # Checks if client is archived and proposes to return it
    elif in_base[2] == 1:
        list_of_buttons = types.InlineKeyboardMarkup(row_width=2)
        return_post_button = types.InlineKeyboardButton(text=messages.track_again,
                                                        callback_data=f'return_client_{in_base[1]}')
        add_another_client_button = types.InlineKeyboardButton(text=messages.add_client_button,
                                                               callback_data='add_new_client')
        nothing_button = types.InlineKeyboardButton(text=messages.nothing,
                                                    callback_data='exit')
        list_of_buttons.add(return_post_button, add_another_client_button, nothing_button)
        bot.send_message(message.chat.id, messages.client_archived, reply_markup=list_of_buttons)

    # Return client_id and propose to add a post for this client as well
    else:
        list_of_buttons = types.InlineKeyboardMarkup(row_width=2)
        add_post_button = types.InlineKeyboardButton(text=messages.add_post,
                                                     callback_data=f'post_add_{in_base[1]}')
        add_another_client_button = types.InlineKeyboardButton(text=messages.add_client_button,
                                                               callback_data='add_new_client')
        nothing_button = types.InlineKeyboardButton(text=messages.nothing,
                                                    callback_data='exit')
        list_of_buttons.add(add_post_button, add_another_client_button, nothing_button)
        bot.send_message(message.chat.id, messages.client_already_exists, reply_markup=list_of_buttons)


@bot.message_handler(content_types=['text'])
def delete_post(message):
    """Deletes post from the base."""
    if message.text == 'STOP':
        bot.send_message(message.chat.id, messages.stop_message)
        return

    if message.text == config.password:
        global post_id
        f.delete_post(post_id)
        post_id = None
        bot.send_message(message.chat.id, messages.deleted_successfully)
    else:
        msg = bot.send_message(message.chat.id, messages.wrong_password)
        bot.register_next_step_handler(msg, delete_post)


@connectionerror
def main():
    logger.debug('Start bot working')
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
