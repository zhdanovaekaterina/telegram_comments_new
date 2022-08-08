import re
from telebot import types
import queries


def generate_buttons_list(callback_case: str, client_id=None):
    """Takes the instruction which callback should be called by buttons.
    Connects to db and generates the list of buttons of clients.
    Returns the list of buttons objects.
    :param: callback_case: the info which callback should be called by buttons;
    :param: client: the id of client, whose posts needed;
    :return: list_of_buttons: the list of buttons.
    """
    result = queries.list_of_elements(callback_case, client_id)
    list_of_buttons = types.InlineKeyboardMarkup()

    for res in result:  # Generate the list of buttons for each result
        button = types.InlineKeyboardButton(text=res[1],
                                            callback_data=f'{callback_case}_{res[0]}')
        list_of_buttons.add(button)
    return list_of_buttons


def get_post_details(post_id):
    """Takes post_id (unique number inside db) and returns info message about the post.
    Also generate post link.
    :param post_id: post id inside database;
    :return: post_info: info message and post link.
    """
    post_info = queries.post_info(post_id)

    post_info_message = f'Название поста: {post_info["post_name"]}\n' \
                        f'Канал: {post_info["channel_name"]}\n' \
                        f'Дата публикации: {post_info["publication_date"]}\n' \
                        f'Подписчиков на момент публикации: {post_info["subscribers_count"]}\n' \
                        f'Просмотров: {post_info["views"]}\n' \
                        f'Реакций: {post_info["reactions"]}\n' \
                        f'Комментариев всего: {post_info["comments_all"]}\n' \
                        f'Новых комментариев: {post_info["comments_new"]}\n'

    post_link = f'https://t.me/{post_info["channel_name"]}/{post_info["channel_post_id"]}'

    return post_info_message, post_link


if __name__ == '__main__':
    pass
