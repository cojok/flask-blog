from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sendgrid import SendGridAPIClient
from flaskBlog.config import Config

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

sg = SendGridAPIClient(Config.SG_KEY)

from flaskBlog.users.routes import users
from flaskBlog.posts.routes import posts
from flaskBlog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)