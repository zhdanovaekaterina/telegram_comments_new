import sqlite3 as sl
import config
import re
from datetime import datetime


def check_client(new_client: str):
    """Checks if new client is already in the base.
    :param: new_client: name of new client, letter case doesn't matter;
    :return: is_in_base: flag if client is already in base;
    :return: client_id: id value if client is in base already, else False;
    """
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    query = """SELECT client_id FROM clients WHERE client_name = ?"""
    param = (new_client.capitalize(),)

    cursor.execute(query, param)
    clients = cursor.fetchall()
    is_in_base = False if len(clients) == 0 else True
    client_id = clients[0][0] if is_in_base else False

    con.close()

    return is_in_base, client_id


def add_client(new_client: str):
    """Adds new client to the base.
    :param new_client: name of new client, letter case doesn't matter - will be capitalized;
    :return: is_added: flag if client added successfully;
    :return: client_id: id value of new client.
    """
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    query = """INSERT INTO clients (client_name, is_archive) VALUES (?, ?)"""
    values = (new_client.capitalize(), 0)
    cursor.execute(query, values)
    con.commit()

    query = """SELECT client_id FROM clients WHERE client_name = ?"""
    values = (new_client.capitalize(),)
    cursor.execute(query, values)
    clients = cursor.fetchall()
    client_id = clients[0][0]

    con.close()

    is_added = True
    return is_added, client_id


def list_of_elements(callback_case: str, client_id=None):
    """Returns a list of elements."""
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    is_archive = 1 if re.fullmatch(r'^.*archive.*$', callback_case) else 0
    if client_id is not None:
        query = f"""SELECT post_id, post_name
                    FROM posts
                    WHERE is_archive = {is_archive} AND client_id = ?
                    """
        params = (client_id,)
        cursor.execute(query, params)
    else:
        query = f"""SELECT client_id, client_name
                    FROM clients
                    WHERE is_archive = {is_archive}
                    """
        cursor.execute(query)

    result = cursor.fetchall()
    con.close()

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

    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    params = (post_id,)

    query_1 = """SELECT channel_name, channel_post_id
            FROM posts
            WHERE post_id = ?
            """

    query_2 = """SELECT comment_date, author, comment_text, is_new
            FROM comments
            WHERE post_id = ?
            """

    cursor.execute(query_1, params)
    post_info = cursor.fetchall()
    cursor.execute(query_2, params)
    comments_info = cursor.fetchall()

    con.close()

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


if __name__ == '__main__':
    comment_info(1)
