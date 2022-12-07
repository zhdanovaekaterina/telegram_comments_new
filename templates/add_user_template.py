from src import config
from classes.database import Database

users_list = [1219345985]  # Here you should put a list of users to add.

if __name__ == '__main__':
    with Database() as db:
        for user in users_list:
            db.add_user(user)
