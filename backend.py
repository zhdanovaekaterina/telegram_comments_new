# This Python file uses the following encoding: ascii
# This module does all dirty work for the program.


import requests
from bs4 import BeautifulSoup
import re
import config
import json
import telethon
import functions as f
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection, client
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon import functions, types
import sqlite3 as sl


client = TelegramClient(config.username, config.api_id, config.api_hash)
client.start()


async def dump_comments(channel, post_id):
    all_messages = []
    async for message in client.iter_messages(channel, reply_to=post_id, reverse=True):
        if isinstance(message.sender, telethon.tl.types.User):
            mess_date = message.date.timestamp()
            new_rec = [mess_date, message.sender.username, message.sender.first_name, message.text]
        else:
            new_rec = None
        all_messages.append(new_rec)

    for i, mess in enumerate(all_messages):
        if all_messages[i] is None:
            del all_messages[i]

    return all_messages


async def dump_post_info(channel, post_id):
    all_messages = []

    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    history = await client(GetHistoryRequest(
        peer=channel,
        offset_id=(post_id+1),
        offset_date=None,
        add_offset=0,
        limit=1, max_id=0, min_id=0,
        hash=0))

    messages = history.messages

    for message in messages:
        all_messages.append(message.to_dict())

    publication_date = all_messages[0]['edit_date']
    views = all_messages[0]['views']
    forwards = all_messages[0]['forwards']
    replies = all_messages[0]['replies']['replies']

    publication_date = publication_date.timestamp()

    all_data = {'publication_date': publication_date,
                'views': views,
                'forwards': forwards,
                'replies': replies}

    return all_data

    # with open('channel_messages.json', 'w', encoding='utf8') as outfile:
    #     json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)


def dump_subscribers_count(channel: str):
    """Takes channel name and returns the number of its subscribers."""
    url = f'https://tgstat.ru/channel/@{channel}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    r = requests.get(url, headers=headers)
    r = r.text

    try:
        # Extract raw subscribers count
        soup = BeautifulSoup(r, 'html.parser').find('h2').get_text()

        # Convert subscribers count to int
        subscribers_count = re.findall(r'\d+', soup)
        subscribers_count = int(''.join(subscribers_count))
    except AttributeError:
        subscribers_count = 0

    return subscribers_count


async def collecting_data(post_id: int, is_first_collecting: bool):
    """Takes post_id and flag if it is first time."""

    # Get post attributes from the base
    query_case = 'select_2'
    elements = ['channel_name', 'channel_post_id', 'posts', 'post_id']
    parametrs = (post_id,)
    post_info = f.query_constructor(query_case, elements, parametrs)

    # Create channel link and channel object
    channel_link = f'https://t.me/{post_info[0][0]}'
    channel = await client.get_entity(channel_link)
    channel_post_id = post_info[0][1]

    # Dump comments
    all_comments = await dump_comments(channel, channel_post_id)

    # Dump post info
    all_data = await dump_post_info(channel, channel_post_id)
    if is_first_collecting:
        all_data['subscribers_count'] = dump_subscribers_count(post_info[0][0])

    return all_data, all_comments


def put_data_tobase(post_id, data, comments, is_first_collecting: bool):

    # Open connection
    con = sl.connect(config.workbase_name)
    cursor = con.cursor()

    # Put data into posts
    if is_first_collecting:
        query = 'UPDATE posts SET publication_date = ?, subscribers_count = ? WHERE post_id = ?'
        parametrs = (data['publication_date'], data['subscribers_count'], post_id)
        cursor.execute(query, parametrs)

    # Put data into stats
    date_now = datetime.now().timestamp()
    query = 'INSERT INTO stats (post_id, date, views, forwards) VALUES (?, ?, ?, ?)'
    parametrs = (post_id, date_now, data['views'], data['forwards'])
    cursor.execute(query, parametrs)

    comments_to_load = []
    if not is_first_collecting:

        # Load all previous comments from the base
        query = 'SELECT comment_date FROM comments WHERE post_id = ?'
        parametrs = (post_id,)
        cursor.execute(query, parametrs)
        old_comments = cursor.fetchall()

        # Compare old and new comment sets
        old_comments = set(*old_comments)
        new_comments = set()
        for comm in comments:
            new_comments.add(comm[0])
        diff_set = new_comments - old_comments

        # Update list of comments to load
        for comm in comments:
            if comm[0] in diff_set:
                comm.insert(0, post_id)
                comm.append('1')
                comm = tuple(comm)
                comments_to_load.append(comm)

    else:
        for comm in comments:
            comm.insert(0, post_id)
            comm.append('1')
            comm = tuple(comm)
            comments_to_load.append(comm)

    # Put comments into comments
    query = 'INSERT INTO comments (post_id, comment_date, author_username, author, comment_text, is_new) ' \
            'VALUES (?, ?, ?, ?, ?, ?)'
    cursor.executemany(query, comments_to_load)

    # Commit and close connection
    con.commit()
    con.close()


async def main():
    post_id = 5  # Test canape post
    is_first_collecting = False  # Test flag
    data, comments = await collecting_data(post_id, is_first_collecting)
    put_data_tobase(post_id, data, comments, is_first_collecting)
    print('Done!')


with client:
    client.loop.run_until_complete(main())
