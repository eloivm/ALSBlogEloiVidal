import uuid
from datetime import datetime

class Comment:
    def __init__(self, content, user_id, post_id, user_nickname):
        self._comment_id = str(uuid.uuid4())
        self._content = content
        self._post_id = post_id
        self._user_id = user_id
        self._user_nickname = user_nickname
        self._created_at = datetime.now()

    @property
    def comment_id(self):
        return self._comment_id

    @property
    def content(self):
        return self._content

    @property
    def user_id(self):
        return self._user_id
    
    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def user_nickname(self):
        return self._user_nickname
    
    @user_nickname.setter
    def user_nickname(self, value):
        self._user_nickname = value

    @property
    def post_id(self):
        return self._post_id

    @property
    def created_at(self):
        return self._created_at