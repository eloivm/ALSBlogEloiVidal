from model.user import User
from model.post import Post
from model.comment import Comment
from srp import srp
import re
from flask_login import LoginManager

def is_valid_nickname(nickname):
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_]{2,19}$'
    return re.match(pattern, nickname) is not None

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_valid_password(password):
    if len(password) < 8:
        return False

    has_lowercase = re.search(r'[a-z]', password) is not None
    has_uppercase = re.search(r'[A-Z]', password) is not None
    has_digit_or_special_char = re.search(r'[\d\W_]', password) is not None

    return has_lowercase and has_uppercase and has_digit_or_special_char

def nickname_exists(nickname):
    lower_nickname = nickname.lower()
    for user_oid in srp.load_all_keys(User):
        loaded_user = srp.load(user_oid)
        if loaded_user.nickname.lower() == lower_nickname:
            return True
    return False

def email_exists(email):
    for user_oid in srp.load_all_keys(User):
        loaded_user = srp.load(user_oid)
        if loaded_user.email == email:
            return True
    return False

def update_posts(old_nickname, new_nickname):
    for post_oid in srp.load_all_keys(Post):
        post = srp.load(post_oid)
        if post.user_id == old_nickname:
            post.user_id = new_nickname
            srp.save(post)

    new_user_id = None
    for user_oid in srp.load_all_keys(User):
        user = srp.load(user_oid)
        if user.nickname == new_nickname:
            new_user_id = user.id
            break

    for comment_oid in srp.load_all_keys(Comment):
        comment = srp.load(comment_oid)
        if comment.user_nickname == old_nickname:
            comment.user_nickname = new_nickname
            comment.user_id = new_user_id
            srp.save(comment)
