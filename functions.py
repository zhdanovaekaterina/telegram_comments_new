import messages
from telebot import types
from test_post_object import TestObject


def generate_buttons_list(callback_case: str, client=None):
    """Takes the instruction which callback should be called by buttons.
    Connects to db and generates the list of buttons of clients.
    Returns the list of buttons objects.
    :param: callback_case: the info which callback should be called by buttons;
    :param: client: the id of client, whose posts needed;
    :return: list_of_buttons: the list of buttons.
    """
    all_clients = ['client1', 'client2', 'client3']  # Temporary 'cap' object
    # TODO: add the connection to db and take the list of objects (query depends on client param and callback case).
    # TODO: Also add different queries for active and archived clients.
    list_of_buttons = types.InlineKeyboardMarkup()
    for client in all_clients:  # Generate the list of buttons for each client
        client_temp = TestObject(client)  # Temporary 'cap' object
        button = types.InlineKeyboardButton(text=client_temp.name,
                                            callback_data=f'{callback_case}_{client_temp.name}')
        list_of_buttons.add(button)
    return list_of_buttons


def get_post_details(post_id):
    """Takes post_id (unique number inside db) and returns dictionary with all detailed info about the post.
    Also generate post link.
    :param post_id: post id inside database;
    :return: post_info: a dictionary with all post information (including link and comments count).
    """
    # TODO: add the connection to db to take all info.
    post_info = {'post_id': '0',    # Temporary 'cap' object
                 'channel_name': 'ChannelName',
                 'post_name': 'PostName',
                 'channel_post_id': '111',
                 'comments': {'comment1': {'comment_id': '0',
                                           'comment_date': '0',
                                           '...': '...'
                                           },
                              '...': {'...': '...'
                                      }
                              }
                 }
    post_info['post_link'] = f'https://t.me/{post_info["channel_name"]}/{post_info["channel_post_id"]}'
    return post_info
