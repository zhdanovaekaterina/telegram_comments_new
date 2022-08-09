import csv
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
        query = """SELECT post_id, post_name
                    FROM posts
                    WHERE is_archive = ? AND client_id = ?
                    """
        params = (is_archive, client_id)
        cursor.execute(query, params)
    else:
        if is_archive == 0:
            query = """SELECT client_id, client_name
                        FROM clients
                        WHERE is_archive = ?
                        """
            params = (is_archive,)
            cursor.execute(query, params)
        else:
            query = """SELECT clients.client_id, clients.client_name
                        FROM clients LEFT JOIN posts USING(client_id)
                        GROUP BY clients.client_id
                        HAVING SUM(posts.is_archive) > 0
                        """
            cursor.execute(query)

    result = cursor.fetchall()
    con.close()

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
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    post_arguments = read_arguments(file_link)

    query = """SELECT post_id FROM posts WHERE channel_name = ? AND channel_post_id = ?"""
    param = (post_arguments['channel_name'], post_arguments['channel_post_id'])

    cursor.execute(query, param)
    posts = cursor.fetchall()
    is_in_base = False if len(posts) == 0 else True
    post_id = posts[0][0] if is_in_base else False

    con.close()

    return is_in_base, post_id


def add_post(file_link: str):
    """Adds new client to the base.
    :param file_link: name of the file which has all arguments;
    :return: is_added: flag if client added successfully;
    :return: post_id: id value of new client.
    """
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    post_arguments = read_arguments(file_link)

    query = """INSERT INTO posts (client_id, channel_name, channel_post_id, post_name, is_archive)
            VALUES (?, ?, ?, ?, ?)
            """
    values = (post_arguments['client_id'], post_arguments['channel_name'], post_arguments['channel_post_id'],
              post_arguments['post_name'], 0)
    cursor.execute(query, values)
    con.commit()

    query = """SELECT post_id FROM posts WHERE channel_name = ? AND channel_post_id = ?"""
    values = (post_arguments['channel_name'], post_arguments['channel_post_id'])
    cursor.execute(query, values)
    clients = cursor.fetchall()
    post_id = clients[0][0]

    con.close()

    is_added = True
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
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    values = (post_id,)
    query = "DELETE FROM posts WHERE post_id = ?"
    cursor.execute(query, values)

    con.commit()
    con.close()


if __name__ == '__main__':
    pass
