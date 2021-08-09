from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from discussionForum.config import Config



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please Login First'
mail = Mail()










def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    from discussionForum.users.routes import users
    from discussionForum.main.routes import main
    from discussionForum.posts.routes import posts
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(posts)
    return app


