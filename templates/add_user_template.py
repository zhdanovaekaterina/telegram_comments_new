from src import config
from classes.database import Database

users_list = [675016848]  # Here you should put a list of users to add.

if __name__ == '__main__':
    db = Database(config.host, config.port, config.user_name, config.user_password)
    for user in users_list:
        db.add_user(user)
