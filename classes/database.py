from mysql.connector import connect, Error


class Database:

    def __init__(self, host, port, user_name, user_password):
        try:
            self.connection = connect(host=host,
                                      port=port,
                                      user=user_name,
                                      password=user_password)
            self.cursor = self.connection.cursor()
        except Error as e:
            print(e)

    def __del__(self):
        self.connection.close()

    def select_query(self, query, params=False):
        self.cursor.execute(query, params) if not params else self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def update_query(self, query, params=False):
        self.cursor.execute(query, params) if not params else self.cursor.execute(query)
        self.connection.commit()

    def update_many_query(self, query, params=False):
        self.cursor.executemany(query, params) if not params else self.cursor.executemany(query)
        self.connection.commit()

    def init_base(self):
        """Creates workbase structure, if it doesn't exist yet."""

        # Create table 'users'
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
                              (user_id INT PRIMARY KEY AUTO_INCREMENT,
                               user_name INT)
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
                            publication_date DATE,
                            subscribers_count INT,
                            is_archive BOOL,
                            FOREIGN KEY client_id REFERENCES clients (client_id) ON DELETE CASCADE
                            );
                           """)

        # Create table 'stats'
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS stats
                              (stat_row_id INT PRIMARY KEY AUTO_INCREMENT,
                               post_id INT,
                               date DATE,
                               views INT,
                               forwards INT,
                               FOREIGN KEY post_id REFERENCES posts (post_id) ON DELETE CASCADE
                               );
                           """)

        # Create table 'comments'
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS comments
                              (comment_id INT PRIMARY KEY AUTO_INCREMENT,
                               post_id INT,
                               comment_date DATE,
                               author_username VARCHAR(50),
                               author VARCHAR(50),
                               comment_text VARCHAR(50),
                               is_new BOOL,
                               FOREIGN KEY post_id REFERENCES posts (post_id) ON DELETE CASCADE
                               );
                           """)