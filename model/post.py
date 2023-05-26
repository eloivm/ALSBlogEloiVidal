import uuid
from datetime import datetime

class Post:
    def __init__(self, title, content, user_id):
        self._post_id = str(uuid.uuid4())
        self._title = title
        self._content = content
        date = datetime.now()
        self._created_at = date
        self._edited_at = date
        self._user_id = user_id

    @property
    def post_id(self):
        return self._post_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._edited_at = datetime.now()

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        self._edited_at = datetime.now()


    @property
    def created_at(self):
        return self._created_at

    @property
    def edited_at(self):
        return self._edited_at

    @property
    def user_id(self):
        return self._user_id
        
    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    def __str__(self):
        return f"{self.title}: \"{self.content}\""