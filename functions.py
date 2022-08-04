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
