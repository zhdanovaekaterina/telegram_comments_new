import os

from dotenv import load_dotenv
load_dotenv()

token = os.getenv('BOT_TOKEN')

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
username = os.getenv('TG_USERNAME')
session = os.getenv('SESSION')
