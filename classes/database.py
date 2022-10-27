import logging
from mysql.connector import connect, Error

from src import config as c

# Logger settings
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
                    force=True,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )


class Database:

    def __init__(self):
        self.host = c.host
        self.port = c.port
        self.user_name = c.user_name
        self.user_password = c.user_password

    def __enter__(self):
        try:
            self._enter()
        except Error as e:
            error_code = str(e).split(' ')[0]
            if error_code == '1049':
                self._init_base()
                self._enter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def _enter(self):
        self.connection = connect(host=self.host,
                                  port=self.port,
                                  user=self.user_name,
                                  password=self.user_password)
        self.cursor = self.connection.cursor()
        self.cursor.execute('USE bot_base')

    def _init_base(self):
        """Creates workbase structure, if it doesn't exist yet."""
        logger.debug('Base init')
        with self:
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS bot_base')
            self.cursor.execute('USE bot_base')

            # Create table 'users'
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
                                  (user_id INT PRIMARY KEY AUTO_INCREMENT,
                                   user_name BIGINT)
                               """)

            # Create table 'clients'
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS clients
                                  (client_id INT PRIMARY KEY AUTO_INCREMENT,
                                   client_name VARCHAR(50),
                                   is_archive BOOL)
                               """)

            # Create table 'posts'
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS posts (
                                post_id INT PRIMARY KEY AUTO_INCREMENT,
                                client_id INT,
                                channel_name VARCHAR(50),
                                channel_post_id INT,
                                post_name VARCHAR(100),
                                publication_date INT,
                                subscribers_count INT,
                                is_archive BOOL,
                                FOREIGN KEY (client_id) REFERENCES clients (client_id) ON DELETE CASCADE);
                               """)

            # Create table 'stats'
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS stats
                                  (stat_row_id INT PRIMARY KEY AUTO_INCREMENT,
                                   post_id INT,
                                   date INT,
                                   views INT,
                                   forwards INT,
                                   FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE
                                   );
                               """)

            # Create table 'comments'
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS comments \
                                  (comment_id INT PRIMARY KEY AUTO_INCREMENT, \
                                   post_id INT, \
                                   comment_date INT, \
                                   author_username VARCHAR(50), \
                                   author VARCHAR(50), \
                                   comment_text VARCHAR({c.comments_length}), \
                                   is_new BOOL, \
                                   FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE \
                                   );')

    def select_query(self, query, params=None):
        logger.debug('Select query')
        if params is not None:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def update_query(self, query, params=None):
        logger.debug('Update query')
        if params is not None:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.connection.commit()

    def update_many_query(self, query, params=None):
        logger.debug('Update many items query')
        if params is not None:
            self.cursor.executemany(query, params)
        else:
            self.cursor.executemany(query)
        self.connection.commit()

    def add_user(self, user_name):
        select_query = 'SELECT user_id FROM users WHERE user_name = %s'
        insert_query = 'INSERT INTO users (user_name) VALUES (%s)'
        params = (user_name,)
        user_id = self.select_query(select_query, params)
        if len(user_id) == 0:
            self.update_query(insert_query, params)
            print('User added successfully.')
        else:
            print('This user is already in base.')
