from flask import Flask
from auth_bp import auth_bp
from posts_bp import posts_bp
from comments_bp import comments_bp
from editProfile_bp import editProfile_bp
from srp import srp
from flask import flash, redirect
from model.user import User
from flask_login import LoginManager

def create_app():
    fapp = Flask(__name__)
    fapp.secret_key = "1e44b3a45067431da85bfe"

    fapp.register_blueprint(auth_bp)
    fapp.register_blueprint(posts_bp)
    fapp.register_blueprint(comments_bp)
    fapp.register_blueprint(editProfile_bp)

    return fapp

app = create_app()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(srp, user_id)

@login_manager.unauthorized_handler
def unauthorized_handler():
    flash("Unauthorized")
    return redirect("/login")
