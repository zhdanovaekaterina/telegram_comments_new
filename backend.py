# This Python file uses the following encoding: ascii
# This module does all dirty work for the program.


from distutils import dist
from requests import post
import config
import json
import telethon
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon import connection, client
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon import functions, types


client = TelegramClient(config.username, config.api_id, config.api_hash)
client.start()


async def dump_comments(channel, post_id):
    async for message in client.iter_messages(channel, reply_to=post_id, reverse=True):
        if isinstance(message.sender, telethon.tl.types.User):
            mess_date = message.date.strftime(config.date_format)
            new_rec = [mess_date, message.sender.username, message.sender.first_name, message.text]
        else:
            new_rec = None
        return new_rec


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

    publication_date = publication_date.strftime(config.date_format)

    all_data = {'publication_date': publication_date,
                'views': views,
                'forwards': forwards,
                'replies': replies}

    return all_data

    # with open('channel_messages.json', 'w', encoding='utf8') as outfile:
    #     json.dump(all_messages, outfile, ensure_ascii=False, cls=DateTimeEncoder)


async def dump_subscribers_count(channel):
    all_info = []

    result = client(GetFullChannelRequest(channel=channel))
    print(result)


def input_url():
    """Takes a link and returns channel and post number."""
    post_input = input("Give me a link to the post: ")
    post_id = int(post_input.split('/')[-1])  # returns post number
    url = post_input.split('/')
    del url[-1]
    url = '/'.join(url) + '/'  # returns channel link
    return url, post_id


async def main():
    url, post_id = input_url()
    channel = await client.get_entity(url)
    comments = await dump_comments(channel, post_id)
    all_data = await dump_post_info(channel, post_id)
    await dump_subscribers_count(channel)
    print('Done!')


with client:
    client.loop.run_until_complete(main())
