class NewPost:
    """Saves the information about new post while all info isn't collected."""

    def __init__(self):
        self.client_id = None
        self.post_name = None
        self.channel_name = None
        self.channel_post_id = None
        self.is_archive = False

    def add_client_id(self, client_id):
        self.client_id = client_id

    def add_post_name(self, post_name):
        self.post_name = post_name

    def add_channel_name(self, channel_name):
        self.channel_name = channel_name

    def add_channel_post_id(self, channel_post_id):
        self.channel_post_id = channel_post_id

    def default_condition(self):
        self.client_id = None
        self.post_name = None
        self.channel_name = None
        self.channel_post_id = None
        self.is_archive = False
