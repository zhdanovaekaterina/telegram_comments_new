from telebot import types
import config
import csv
import sqlite3 as sl
import re
from datetime import datetime


def init_base():
    """Creates workbase structure, if it doesn't exist yet."""
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    # Enable foreign keys
    cursor.execute("""PRAGMA foreign_keys=on""")

    # Create table 'clients'
    cursor.execute("""CREATE TABLE IF NOT EXISTS clients
                      (client_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       client_name TEXT,
                       is_archive INTEGER)
                   """)

    # Create table 'posts'
    cursor.execute("""CREATE TABLE IF NOT EXISTS posts (
                    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    channel_name TEXT,
                    channel_post_id INTEGER,
                    post_name TEXT,
                    publication_date INTEGER,
                    subscribers_count INTEGER,
                    is_archive INTEGER,
                    views INTEGER,
                    reactions INTEGER,
                    CONSTRAINT posts_FK FOREIGN KEY (client_id) REFERENCES clients(client_id)
                    );
                   """)

    # Create table 'stats'
    cursor.execute("""CREATE TABLE IF NOT EXISTS stats
                      (stat_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       post_id INTEGER,
                       start_date INTEGER,
                       end_date INTEGER,
                       CONSTRAINT stats_FK FOREIGN KEY (post_id) REFERENCES posts(post_id)
                       );
                   """)

    # Create table 'comments'
    cursor.execute("""CREATE TABLE IF NOT EXISTS comments
                      (comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       post_id INTEGER,
                       comment_date INTEGER,
                       author TEXT,
                       comment_text TEXT,
                       is_new INTEGER,
                       CONSTRAINT comments_FK FOREIGN KEY (post_id) REFERENCES posts(post_id)
                       );
                   """)

    con.commit()
    con.close()


def query_constructor(query_type: str, elements: list, parametrs: tuple):
    """Query constructor."""

    # * = query construct elements; ? = params
    query_types = {'select_1': 'SELECT * FROM * WHERE * = ?',
                   'select_2': 'SELECT *, * FROM * WHERE * = ?',
                   'select_3': 'SELECT * FROM * WHERE * = ? AND * = ?',
                   'select_4': 'SELECT *, * FROM * WHERE * = ? AND * = ?',
                   'select_5': 'SELECT *, * FROM * LEFT JOIN * USING(*) GROUP BY * HAVING * > ?',
                   'select_6': 'SELECT *, *, *, * FROM * WHERE * = ?',
                   'update_1': 'UPDATE * SET * = ? WHERE * = ?',
                   'insert_1': 'INSERT INTO * (*, *) VALUES (?, ?)',
                   'insert_2': 'INSERT INTO * (*, *, *, *, *) VALUES (?, ?, ?, ?, ?)',
                   'delete_1': 'DELETE FROM * WHERE * = ?'}

    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    query = query_types[query_type]

    for el in elements:
        query = re.sub(r'\*', el, query, count=1)

    cursor.execute(query, parametrs)

    if re.fullmatch(r'^select.*', query_type):
        result = cursor.fetchall()
    else:
        result = True
        con.commit()

    con.close()
    return result


def check_client(new_client: str):
    """Checks if new client is already in the base.
    :param: new_client: name of new client, letter case doesn't matter;
    :return: is_in_base: flag if client is already in base;
    :return: client_id: id value if client is in base already, else False;
    """
    query_case = 'select_1'
    elements = ['client_id', 'clients', 'client_name']
    parametrs = (new_client.capitalize(),)
    result = query_constructor(query_case, elements, parametrs)

    is_in_base = False if len(result) == 0 else True
    client_id = result[0][0] if is_in_base else False

    return is_in_base, client_id


def add_client(new_client: str):
    """Adds new client to the base.
    :param new_client: name of new client, letter case doesn't matter - will be capitalized;
    :return: is_added: flag if client added successfully;
    :return: client_id: id value of new client.
    """
    query_case = 'insert_1'
    elements = ['clients', 'client_name', 'is_archive']
    parametrs = (new_client.capitalize(), 0)
    is_added = query_constructor(query_case, elements, parametrs)

    query_case = 'select_1'
    elements = ['client_id', 'clients', 'client_name']
    parametrs = (new_client.capitalize(),)
    result = query_constructor(query_case, elements, parametrs)
    client_id = result[0][0]

    return is_added, client_id


def list_of_elements(callback_case: str, client_id=None):
    """Returns a list of elements."""

    is_archive = 1 if re.fullmatch(r'^.*archive.*$', callback_case) else 0
    if client_id is not None:
        query_case = 'select_4'
        elements = ['post_id', 'post_name', 'posts', 'is_archive', 'client_id']
        parametrs = (is_archive, client_id)
        result = query_constructor(query_case, elements, parametrs)
    else:
        if is_archive == 0:
            query_case = 'select_2'
            elements = ['client_id', 'client_name', 'clients', 'is_archive']
            parametrs = (is_archive,)
            result = query_constructor(query_case, elements, parametrs)
        else:
            query_case = 'select_5'
            elements = ['clients.client_id', 'clients.client_name', 'clients', 'posts', 'client_id',
                        'clients.client_id', 'posts.is_archive']
            parametrs = (0,)
            result = query_constructor(query_case, elements, parametrs)

    if len(result) == 0:
        result = None

    return result


def post_info(post_id: int):
    """Takes post_id (unique number inside db) and returns dictionary with all detailed info about the post.
    :param: post_id: post id inside database;
    :return: post_info: a dictionary with all post information.
    """
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    query = """SELECT channel_name, channel_post_id, post_name, publication_date, subscribers_count, views, reactions,
                    (SELECT COUNT(comment_id)
                    FROM comments
                    WHERE post_id = ?
                    GROUP BY post_id) as comments_all,
                    (SELECT COUNT(comment_id)
                    FROM comments
                    WHERE post_id = ? AND is_new = 1
                    GROUP BY post_id) as comments_new
            FROM posts
            WHERE post_id = ?
            """
    params = (post_id, post_id, post_id)

    cursor.execute(query, params)
    result = cursor.fetchall()
    con.close()

    # Convert answer to dictionary
    result_keys = ['channel_name', 'channel_post_id', 'post_name', 'publication_date', 'subscribers_count', 'views',
                   'reactions', 'comments_all', 'comments_new']
    result_values = list(*result)
    result_dict = dict(zip(result_keys, result_values))

    return result_dict


def comment_info(post_id: int):
    """Takes post_id (unique number inside db) and returns its comments. Also returns post link.
    :param: post_id: post id inside database;
    :return: comments_info_message: message with date, author and text for each comment;
    :return: post_link: direct link to channel.
    """
    result = []

    parametrs = (post_id,)

    query_case_1 = 'select_2'
    elements_1 = ['channel_name', 'channel_post_id', 'posts', 'post_id']
    post_info = query_constructor(query_case_1, elements_1, parametrs)

    query_case_2 = 'select_6'
    elements_2 = ['comment_date', 'author', 'comment_text', 'is_new', 'comments', 'post_id']
    comments_info = query_constructor(query_case_2, elements_2, parametrs)

    # Convert post info to dictionary
    post_result_keys = ['channel_name', 'channel_post_id']
    post_result_values = list(*post_info)
    post_result_dict = dict(zip(post_result_keys, post_result_values))
    result.append(post_result_dict)

    # Convert comments info to list
    result_temp = []
    for i, comm in enumerate(comments_info):
        correct_date = datetime.utcfromtimestamp(comm[0]).strftime('%Y-%m-%d %H:%M')
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


def check_post(file_link: str):
    """Checks if new post is already in the base.
    :param: file_link: name of the file which has all arguments;
    :return: is_in_base: flag if client is already in base;
    :return: client_id: returns if client value is in base already, else False;
    """
    query_case = 'select_3'
    elements = ['post_id', 'posts', 'channel_name', 'channel_post_id']
    post_arguments = read_arguments(file_link)
    parametrs = (post_arguments['channel_name'], post_arguments['channel_post_id'])
    posts = query_constructor(query_case, elements, parametrs)

    is_in_base = False if len(posts) == 0 else True
    post_id = posts[0][0] if is_in_base else False

    return is_in_base, post_id


def add_post(file_link: str):
    """Adds new client to the base.
    :param file_link: name of the file which has all arguments;
    :return: is_added: flag if client added successfully;
    :return: post_id: id value of new client.
    """
    query_case = 'insert_2'
    elements = ['posts', 'client_id', 'channel_name', 'channel_post_id', 'post_name', 'is_archive']
    post_arguments = read_arguments(file_link)
    parametrs = (post_arguments['client_id'], post_arguments['channel_name'], post_arguments['channel_post_id'],
                 post_arguments['post_name'], 0)
    is_added = query_constructor(query_case, elements, parametrs)

    query_case = 'select_3'
    elements = ['post_id', 'posts', 'channel_name', 'channel_post_id']
    post_arguments = read_arguments(file_link)
    parametrs = (post_arguments['channel_name'], post_arguments['channel_post_id'])
    clients = query_constructor(query_case, elements, parametrs)
    post_id = clients[0][0]

    return is_added, post_id


def track_status(post_id: int, to_archive: bool):
    """The procedure, returns the post into the active or archive state (depend on switch flag).
    Checks if it was the last client's post and returns client to active or archive state if so as well."""
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    to_archive = 1 if to_archive else 0

    values_0 = (post_id,)
    query_0 = """SELECT client_id FROM posts WHERE post_id = ?"""
    cursor.execute(query_0, values_0)
    client_id = cursor.fetchall()

    # Update archive status of the post
    values_1 = (to_archive, post_id)
    query_1 = """UPDATE posts SET is_archive = ? WHERE post_id = ?"""
    cursor.execute(query_1, values_1)

    # Check if client have another archived posts
    values_2 = (client_id[0][0],)
    query_2 = """SELECT SUM(is_archive), COUNT(post_id) FROM posts WHERE client_id = ?"""
    cursor.execute(query_2, values_2)
    client_archive_posts = cursor.fetchall()

    is_archive_client = 1 if client_archive_posts[0][0] == client_archive_posts[0][1] else 0

    # Update archive status of the client
    values_3 = (is_archive_client, client_id[0][0],)
    query_3 = """UPDATE clients SET is_archive = ? WHERE client_id = ?"""
    cursor.execute(query_3, values_3)

    # TODO: add flag if removed successfully, else - info message
    con.commit()
    con.close()


def archive_client(client_id: int):
    """Procedure, updates is_archive flag for the client and all its posts."""
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    # Select all active posts of the client
    values_1 = (client_id,)
    query_1 = """SELECT post_id FROM posts WHERE client_id IN(?) AND is_archive = 0"""
    cursor.execute(query_1, values_1)
    clients_active_posts = cursor.fetchall()
    clients_active_posts = [val[0] for val in clients_active_posts]

    # Update archive status for all active posts of the client
    for post in clients_active_posts:
        values_2 = (post,)
        query_2 = """UPDATE posts SET is_archive = 1 WHERE post_id = ?"""
        cursor.execute(query_2, values_2)

    # Update archive status for the client
    query_3 = """UPDATE clients SET is_archive = 1 WHERE client_id = ?"""
    cursor.execute(query_3, values_1)

    con.commit()
    con.close()


def delete_post(post_id: int):
    """Procedure, finally deletes the post from base.
    :param: post_id: unique id of post inside the base.
    """

    query_case = 'delete_1'
    elements = ['posts', 'post_id']
    parametrs = (post_id,)
    query_constructor(query_case, elements, parametrs)


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

    post_info_message = f'Название поста: {post_inf["post_name"]}\n' \
                        f'Канал: {post_inf["channel_name"]}\n' \
                        f'Дата публикации: {post_inf["publication_date"]}\n' \
                        f'Подписчиков на момент публикации: {post_inf["subscribers_count"]}\n' \
                        f'Просмотров: {post_inf["views"]}\n' \
                        f'Реакций: {post_inf["reactions"]}\n' \
                        f'Комментариев всего: {post_inf["comments_all"]}\n' \
                        f'Новых комментариев: {post_inf["comments_new"]}\n'

    post_link = f'https://t.me/{post_inf["channel_name"]}/{post_inf["channel_post_id"]}'

    return post_info_message, post_link


if __name__ == '__main__':
    pass
