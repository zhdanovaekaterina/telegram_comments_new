# This Python file uses the following encoding: ascii
# This module does all dirty work for the program.
import json
import re
from datetime import datetime

import requests
import telethon
import schedule
import telebot
from bs4 import BeautifulSoup
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

import src.config as c
from modules import functions as f
from classes.database import Database
# from bot_main import main as bot_func


tg_client = TelegramClient(c.username, c.api_id, c.api_hash)
# tg_client.start()


async def dump_comments(channel, post_id):
    # Error processing if channel comments turned off
    try:
        all_messages = []
        async for message in tg_client.iter_messages(channel, reply_to=post_id, reverse=True):
            if isinstance(message.sender, telethon.tl.types.User):
                mess_date = message.date.timestamp()
                comm_length = c.comments_length - 5
                message_text = message.text[:comm_length] + '...' if len(message.text) > comm_length else message.text
                new_rec = [mess_date, message.sender.username, message.sender.first_name, message_text]
            else:
                new_rec = None
            all_messages.append(new_rec)

        for i, mess in enumerate(all_messages):
            if all_messages[i] is None:
                del all_messages[i]

    except telethon.errors.rpcerrorlist.MsgIdInvalidError:
        all_messages = None

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

    history = await tg_client(GetHistoryRequest(
        peer=channel,
        offset_id=(post_id + 1),
        offset_date=None,
        add_offset=0,
        limit=1, max_id=0, min_id=0,
        hash=0))

    messages = history.messages

    for message in messages:
        all_messages.append(message.to_dict())

    # Check if the ID received match the ID asked
    if all_messages[0]['id'] != post_id:
        all_data = False
    else:
        publication_date = all_messages[0]['date']
        views = all_messages[0]['views']
        forwards = all_messages[0]['forwards']

        publication_date = publication_date.timestamp()

        all_data = {'publication_date': publication_date,
                    'views': views,
                    'forwards': forwards}

    return all_data


def dump_subscribers_count(channel_name: str):
    """Takes channel name and returns the number of its subscribers."""
    url = f'https://tgstat.ru/channel/@{channel_name}'
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


async def collecting_data(post: list):
    """Takes post_id and flag if it is first time."""

    # Create channel link and channel object
    channel_link = f'https://t.me/{post[0][1]}'
    channel = await tg_client.get_entity(channel_link)
    channel_post_id = post[0][2]

    # Dump comments
    all_comments = await dump_comments(channel, channel_post_id)

    # Dump post info
    all_data = await dump_post_info(channel, channel_post_id)
    if not all_data:
        f.track_status(post[0], to_archive=True)

    if post[1]:
        all_data['subscribers_count'] = dump_subscribers_count(post[0][1])

    return all_data, all_comments


def put_data_to_posts(post_id, data):
    query = 'UPDATE posts SET publication_date = %s, subscribers_count = %s WHERE post_id = %s'
    params = (data['publication_date'], data['subscribers_count'], post_id)

    with Database() as db:
        db.update_query(query, params)


def put_data_to_stats(post_id, data):
    # Take last added data from base
    query = 'SELECT views, forwards FROM stats WHERE post_id = %s'
    params = (post_id,)

    with Database() as db:
        old_data = db.select_query(query, params)

    # Put data into stats
    if len(old_data) > 0:
        if old_data[-1][0] == data['views'] and old_data[-1][1] == data['forwards']:
            pass
    else:
        date_now = datetime.now().timestamp()
        query = 'INSERT INTO stats (post_id, date, views, forwards) VALUES (%s, %s, %s, %s)'
        params = (post_id, date_now, data['views'], data['forwards'])

        with Database() as db:
            db.update_query(query, params)


def put_data_to_comments(post_id, comments, is_first_collecting: bool):
    comments_to_load = []
    if not is_first_collecting:

        # Load all previous comments from the base
        query = 'SELECT comment_date FROM comments WHERE post_id = %s'
        params = (post_id,)

        with Database() as db:
            old_comments = db.select_query(query, params)

        # Compare old and new comment sets
        old_comments_1 = set()
        [old_comments_1.add(comm[0]) for comm in old_comments]

        new_comments = set()
        [new_comments.add(comm[0]) for comm in comments]
        diff_set = new_comments - old_comments_1

        # Update list of comments to load
        for comm in comments:
            if comm[0] in diff_set:
                comm.insert(0, post_id)
                comm.append('1')
                comm = tuple(comm)
                comments_to_load.append(comm)

    else:
        comments_to_load = []
        for comm in comments:
            comm.insert(0, post_id)
            comm.append('1')
            comm = tuple(comm)
            comments_to_load.append(comm)

    # Put comments into comments
    query = 'INSERT INTO comments (post_id, comment_date, author_username, author, comment_text, is_new) ' \
            'VALUES (%s, %s, %s, %s, %s, %s)'

    with Database() as db:
        db.update_many_query(query, comments_to_load)


def put_data_tobase(post_id, data, comments, is_first_collecting: bool):
    if is_first_collecting:
        put_data_to_posts(post_id, data)

    put_data_to_stats(post_id, data)

    if comments is not None:
        put_data_to_comments(post_id, comments, is_first_collecting)


def get_active_post_list():
    # Get post attributes from the base
    query = 'SELECT post_id, channel_name, channel_post_id, publication_date FROM posts WHERE is_archive = 0'
    with Database() as db:
        post_info = db.select_query(query)

    full_data = []
    for post in post_info:
        full_post = []
        is_first_collecting = False if post[3] is not None else True
        full_post.append(post)
        full_post.append(is_first_collecting)
        full_data.append(full_post)

    return full_data


def send_comments():
    # Create bot connection
    bot = telebot.TeleBot(c.bot_token)
    bot.delete_webhook()

    # Main activity
    result = f.prepare_comments()
    if result.flag:
        for user in result.list_of_users:
            bot.send_message(user, result.notification_message, reply_markup=result.list_of_buttons)


def main_main_main():

    with tg_client:
        tg_client.loop.run_until_complete(main())
    send_comments()
    print(f'Done at {datetime.now().strftime("%H:%M")}')


def with_tg_client(main):

    def another_main():
        def main_main_main():

            with tg_client:
                tg_client.loop.run_until_complete(main())
            send_comments()
            print(f'Done at {datetime.now().strftime("%H:%M")}')

        # schedule.every(15).minutes.do(main_main_main)
        schedule.every(15).minutes.do(main_main_main)
        while True:
            schedule.run_pending()

    return another_main


@with_tg_client
async def main():
    print('Start backend working (internal message)')

    # Get all active posts from the base
    full_data = get_active_post_list()

    for post in full_data:
        data, comments = await collecting_data(post)
        if not data:
            continue
        put_data_tobase(post[0][0], data, comments, post[1])


if __name__ == '__main__':
    print('Start backend working!')
    main()
