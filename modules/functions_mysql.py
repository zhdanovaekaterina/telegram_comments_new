import re
import csv
from datetime import datetime

from telebot import types

import config
from classes.database import Database


def check_client(db: Database, new_client: str):
    """Checks if new client is already in the base.
    :param: new_client: name of new client, letter case doesn't matter;
    :return: is_in_base: flag if client is already in base;
    :return: client_id: id value if client is in base already, else False;
    """
    query = """SELECT client_id FROM clients WHERE client_name IN(%s)"""
    params = (str(new_client.capitalize()),)
    result = db.select_query(query, params)

    is_in_base = False if len(result) == 0 else True
    client_id = result[0][0] if is_in_base else False

    return is_in_base, client_id


# TODO: check add_client calls and remove is_added argument (result[0])
def add_client(db: Database, new_client: str):
    """Adds new client to the base.
    :param new_client: name of new client, letter case doesn't matter - will be capitalized;
    :return: is_added: flag if client added successfully;
    :return: client_id: id value of new client.
    """
    query = 'INSERT INTO clients (client_name, is_archive) VALUES (%s, %s)'
    params = (str(new_client.capitalize()), 0)
    db.update_query(query, params)

    query = 'SELECT client_id FROM clients WHERE client_name = %s'
    params = (new_client.capitalize(),)
    result = db.select_query(query, params)
    client_id = result[0][0]

    return client_id


def list_of_elements(callback_case: str, client_id=None):
    """Returns a list of elements."""

    db = Database(config.host, config.port, config.user_name, config.user_password)

    is_archive = 1 if re.fullmatch(r'^.*archive.*$', callback_case) else 0
    if client_id is not None:
        query = 'SELECT post_id, post_name FROM posts WHERE is_archive = %s AND client_id = %s'
        params = (is_archive, client_id)
        result = db.select_query(query, params)
    else:
        # TODO: check if is_archive condition returns correct result
        if is_archive == 0:
            query = 'SELECT client_id, client_name FROM clients WHERE is_archive = 0'
        else:
            query = 'SELECT clients.client_id, clients.client_name ' \
                    'FROM clients LEFT JOIN posts ON clients.client_id = posts.client_id ' \
                    'GROUP BY clients.client_id HAVING SUM(posts.is_archive) > 0'
        result = db.select_query(query)

    del db

    if len(result) == 0:
        result = None

    return result


def post_info(post_id: int):
    """Takes post_id (unique number inside db) and returns dictionary with all detailed info about the post.
    :param: post_id: post id inside database;
    :return: post_info: a dictionary with all post information.
    """
    db = Database(config.host, config.port, config.user_name, config.user_password)

    query = """SELECT channel_name, channel_post_id, post_name, publication_date, subscribers_count,
                    (SELECT views FROM stats WHERE post_id = %s ORDER BY views DESC LIMIT 1) as views,
                    (SELECT forwards FROM stats WHERE post_id = %s ORDER BY forwards DESC LIMIT 1) as forwards,
                    (SELECT COUNT(comment_id) FROM comments WHERE post_id = %s GROUP BY post_id) as comments_all,
                    (SELECT COUNT(comment_id) FROM comments WHERE post_id = %s AND is_new = 1 GROUP BY post_id)
                        as comments_new
            FROM posts
            WHERE post_id = %s
            """
    params = (post_id, post_id, post_id, post_id, post_id)
    result = db.select_query(query, params)
    del db

    # Convert answer to dictionary
    result_keys = ['channel_name', 'channel_post_id', 'post_name', 'publication_date', 'subscribers_count',
                   'views', 'forwards', 'comments_all', 'comments_new']
    result_values = list(*result)
    result_dict = dict(zip(result_keys, result_values))

    if result_dict['publication_date'] is not None:
        pass
    else:
        result_dict = None

    return result_dict


def comment_info(db: Database, post_id: int, need_only_new=0):
    """Takes post_id (unique number inside db) and returns its comments. Also returns post link.
    :param: post_id: post id inside database;
    :return: comments_info_message: message with date, author and text for each comment;
    :return: post_link: direct link to channel.
    """
    result = []

    query = 'SELECT channel_name, channel_post_id FROM posts WHERE post_id = %s'
    params = (post_id,)
    post_info = db.select_query(query, params)

    if len(post_info) == 0:
        return None

    if need_only_new == 1:
        query = 'SELECT comment_date, author, comment_text FROM comments WHERE post_id = %s AND is_new = %s'
        params = (post_id, 1)
    else:
        query = 'SELECT comment_date, author, comment_text, is_new FROM comments WHERE post_id = %s'
        params = (post_id,)

    comments_info = db.select_query(query, params)
    if len(comments_info) == 0:
        return None

    # Convert post info to dictionary
    post_result_keys = ['channel_name', 'channel_post_id']
    post_result_values = list(*post_info)
    post_result_dict = dict(zip(post_result_keys, post_result_values))
    result.append(post_result_dict)

    # Convert comments info to list
    result_temp = []
    for i, comm in enumerate(comments_info):
        correct_date = datetime.utcfromtimestamp(comm[0]).strftime(config.date_format)
        comment_message = f'{correct_date}: {comm[1]}: {comm[2]}'
        result_temp.append(comment_message)
    result.append(result_temp)

    comments_info_message = '\n'.join(result[1])
    post_link = f'https://t.me/{result[0]["channel_name"]}/{result[0]["channel_post_id"]}'

    return comments_info_message, post_link


def read_arguments(file_link: str):
    """Reads all arguments in temporary file and returns a dict with args.
    :param: file_link: ame of the file which has all arguments;
    :return: post_arguments: a dictionary with all post info, saved in file earlier.
    """
    post_arguments = {}
    with open(file_link, 'r') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        for row in csv_reader:
            post_arguments['client_id'] = row[0]
            post_arguments['post_name'] = row[1]
            post_arguments['channel_name'] = row[2]
            post_arguments['channel_post_id'] = row[3]
    return post_arguments


def check_post(db: Database, file_link: str):
    """Checks if new post is already in the base.
    :param: file_link: name of the file which has all arguments;
    :return: is_in_base: flag if client is already in base;
    :return: client_id: returns if client value is in base already, else False;
    """
    query = 'SELECT post_id FROM posts WHERE channel_name = %s AND channel_post_id = %s'
    post_arguments = read_arguments(file_link)
    params = (post_arguments['channel_name'], post_arguments['channel_post_id'])
    posts = db.select_query(query, params)

    is_in_base = False if len(posts) == 0 else True
    post_id = posts[0][0] if is_in_base else False

    return is_in_base, post_id


# TODO: check add_client calls and remove is_added argument (result[0])
def add_post(db: Database, file_link: str):
    """Adds new client to the base.
    :param file_link: name of the file which has all arguments;
    :return: is_added: flag if client added successfully;
    :return: post_id: id value of new client.
    """
    args = read_arguments(file_link)

    query = 'INSERT INTO posts (client_id, channel_name, channel_post_id, post_name, is_archive)' \
            'VALUES (%s, %s, %s, %s, %s)'
    params = (args['client_id'], args['channel_name'], args['channel_post_id'], args['post_name'], 0)
    db.update_query(query, params)


def track_status(post_id: int, to_archive: bool, db=None):
    """The procedure, returns the post into the active or archive state (depend on switch flag).
    Checks if it was the last client's post and returns client to active or archive state if so as well."""
    to_archive = 1 if to_archive else 0
    if db is None:
        db = Database(config.host, config.port, config.user_name, config.user_password)

    query = 'SELECT client_id FROM posts WHERE post_id = %s'
    params = (post_id,)
    client_id = db.select_query(query, params)

    # Update archive status of the post
    query = 'UPDATE posts SET is_archive = %s WHERE post_id = %s'
    params = (to_archive, post_id)
    db.update_query(query, params)

    # Check if client have another archived posts
    query = 'SELECT SUM(is_archive), COUNT(post_id) FROM posts WHERE client_id = %s'
    params = (client_id[0][0],)
    client_archive_posts = db.select_query(query, params)

    is_archive_client = 1 if client_archive_posts[0][0] == client_archive_posts[0][1] else 0

    # Update archive status of the client
    query = 'UPDATE clients SET is_archive = %s WHERE client_id = %s'
    params = (is_archive_client, client_id[0][0],)
    db.update_query(query, params)


def archive_client(client_id: int):
    """Procedure, updates is_archive flag for the client and all its posts."""
    db = Database(config.host, config.port, config.user_name, config.user_password)

    # Select all active posts of the client
    query = 'SELECT post_id FROM posts WHERE client_id IN(%s) AND is_archive = 0'
    params = (client_id,)
    clients_active_posts = db.select_query(query, params)
    clients_active_posts = [val[0] for val in clients_active_posts]

    # Update archive status for all active posts of the client
    for post in clients_active_posts:
        query = 'UPDATE posts SET is_archive = 1 WHERE post_id = %s'
        params_1 = (post,)
        db.update_query(query, params_1)

    # Update archive status for the client
    query = 'UPDATE clients SET is_archive = 1 WHERE client_id = %s'
    db.update_query(query, params)

    del db


def delete_post(db: Database, post_id: int):
    """Procedure, finally deletes the post from base.
    :param: post_id: unique id of post inside the base.
    """
    query = 'DELETE FROM posts WHERE post_id = %s'
    params = (post_id,)
    db.update_query(query, params)


def generate_buttons_list(callback_case: str, client_id=None):
    """Takes the instruction which callback should be called by buttons.
    Connects to db and generates the list of buttons of clients.
    Returns the list of buttons objects.
    :param: callback_case: the info which callback should be called by buttons;
    :param: client: the id of client, whose posts needed;
    :return: list_of_buttons: the list of buttons or None (if list is empty).
    """
    result = list_of_elements(callback_case, client_id)
    list_of_buttons = types.InlineKeyboardMarkup()

    if result is not None:
        for res in result:  # Generate the list of buttons for each result
            button = types.InlineKeyboardButton(text=res[1],
                                                callback_data=f'{callback_case}_{res[0]}')
            list_of_buttons.add(button)
        return list_of_buttons
    else:
        return result


def get_post_details(post_id):
    """Takes post_id (unique number inside db) and returns info message about the post.
    Also generate post link.
    :param post_id: post id inside database;
    :return: post_info: info message and post link.
    """
    post_inf = post_info(post_id)

    if post_inf is not None:
        publication_date = datetime.utcfromtimestamp(post_inf['publication_date']).strftime(config.date_format)

        post_info_message = f'Название поста: {post_inf["post_name"]}\n' \
                            f'Канал: {post_inf["channel_name"]}\n' \
                            f'Дата публикации: {publication_date}\n' \
                            f'Подписчиков на момент публикации: {post_inf["subscribers_count"]}\n' \
                            f'Просмотров: {post_inf["views"]}\n' \
                            f'Репостов: {post_inf["forwards"]}\n' \
                            f'Комментариев всего: {post_inf["comments_all"]}\n'

        post_link = f'https://t.me/{post_inf["channel_name"]}/{post_inf["channel_post_id"]}'
    else:
        post_info_message = 'Для этого поста информация еще не собрана. ' \
                            'Пожалуйста, подождите 15 минут и повторите запрос.'
        post_link = None

    return post_info_message, post_link


def list_of_user_ids(db=None):
    """Procedure which returns actual white list of users."""
    if db is None:
        db = Database(config.host, config.port, config.user_name, config.user_password)
    query = 'SELECT user_name FROM users'
    raw_users = db.select_query(query)
    list_of_users = [int(user[0]) for user in raw_users]
    del db
    return list_of_users


def add_user(db: Database, params):
    """Procedure which adds user to white list."""
    query = 'INSERT INTO users (user_name) VALUES (%s)'
    db.update_query(query, params)


def your_user_id(user_id):
    message = f'При обращении назовите свой user_id: {user_id}'
    return message


def get_new_comments(db: Database):
    """Connect the base and get the list of new comments.
    Returns info message and list of post ids where there are some updates."""

    query = 'SELECT post_id, client_name, post_name, COUNT(comment_id) ' \
            'FROM comments LEFT JOIN posts USING(post_id) LEFT JOIN clients USING(client_id) ' \
            'WHERE comments.is_new = 1 ' \
            'GROUP BY client_name, post_name, post_id'
    raw_new_comments = db.select_query(query)

    have_updates = False if raw_new_comments == [] else True
    return raw_new_comments, have_updates


def compose_notification_message(raw_new_comments):
    time_now = datetime.now().strftime('%H:%M')
    comments_info_message = [f'Сводка на {time_now}\nУ некоторых клиентов есть новые комментарии под постами:\n']
    all_clients = set([post[1] for post in raw_new_comments])
    for client in all_clients:
        all_client_comments = []
        for post in raw_new_comments:
            if post[1] == client:
                temp_message = f'{post[2]}: +{post[3]}'
                all_client_comments.append(temp_message)
        comments = '\n'.join(all_client_comments)
        comments_client_info_message = f'{client}:\n' \
                                       f'{comments}\n'
        comments_info_message.append(comments_client_info_message)
    comments_info_message.append('Чтобы проверить обновления, выберите пост в списке ниже.')

    comments_info_message = '\n'.join(comments_info_message)
    return comments_info_message


def prepare_comments():

    db = Database(config.host, config.port, config.user_name, config.user_password)
    raw_comments, have_updates = get_new_comments(db)
    if have_updates:
        notification_message = compose_notification_message(raw_comments)
        list_of_users = list_of_user_ids(db)
        list_of_buttons = types.InlineKeyboardMarkup()
        for post in raw_comments:
            button = types.InlineKeyboardButton(text=f'{post[1]} - {post[2]}',
                                                callback_data=f'give_comments_list_1_{post[0]}')
            list_of_buttons.add(button)
        flag = True

    else:
        flag, list_of_users, notification_message, list_of_buttons = False, False, False, False

    del db
    return flag, list_of_users, notification_message, list_of_buttons


def delete_is_new_flags(db: Database, post_id):
    """Takes list of post_id's and mark all its comments as read."""
    query = 'UPDATE comments SET is_new = %s WHERE post_id = %s'
    params = (0, post_id)
    db.update_query(query, params)


def delete_all_users(db: Database):
    """Delete all users from the white list."""
    query = 'DELETE FROM users'
    db.update_query(query)


if __name__ == '__main__':
    db = Database(config.host, config.port, config.user_name, config.user_password)
