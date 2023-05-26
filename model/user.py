import uuid
from flask_login import UserMixin
import sirope
from flask_login import current_user, logout_user
class User(UserMixin):
    def __init__(self, nickname, email, password):
        self.id = str(uuid.uuid4())
        self.nickname = nickname
        self.email = email
        self.password = password

    def get_id(self):
        return self.id

    def get_nickname(self):
        return self.nickname

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def __str__(self):
        return f'User(nickname={self.nickname}, email={self.email})'
    
    @staticmethod
    def current_user():
        usr = current_user
        if usr.is_anonymous:
            logout_user()
            usr = None
        return usr
    
    @staticmethod
    def find_by_id(s: sirope.Sirope, id: str) -> "User":
        return s.find_first(User, lambda u: u.get_id() == id)

