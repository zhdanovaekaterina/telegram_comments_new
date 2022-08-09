import csv
import sqlite3 as sl
import config
import re
from datetime import datetime

# * = query construct elements; ? = params
query_types = {'select_1': 'SELECT * FROM * WHERE * = ?',
               'select_2': 'SELECT *, * FROM * WHERE * = ?',
               'select_3': 'SELECT * FROM * WHERE * = ? AND * = ?',
               'select_4': 'SELECT *, * FROM * WHERE * = ? AND * = ?',
               'select_5': 'SELECT *.*, *.* FROM * LEFT JOIN * USING(*) GROUP BY *.* HAVING * > ?',
               'select_6': 'SELECT *, *, *, * FROM * WHERE * = ?',
               'update_1': 'UPDATE * SET * = ? WHERE * = ?',
               'insert_1': 'INSERT INTO * (*, *) VALUES (?, ?)',
               'insert_2': 'INSERT INTO * (*, *, *, *, *) VALUES (?, ?, ?, ?, ?)',
               'delete_1': 'DELETE FROM * WHERE * = ?'}

different_query = """SELECT channel_name, channel_post_id, post_name, publication_date, subscribers_count, views, reactions,
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


def query_constructor(query_type: str, elements: list, parametrs: tuple):
    """Query constructor."""
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    query = query_types[query_type]
    # TODO: add regex.replace * to elements in query template
    cursor.execute(query, parametrs)

    if re.fullmatch(r'^select.*', query_type):
        result = cursor.fetchall()
    else:
        result = True
        con.commit()

    con.close()
    return result
