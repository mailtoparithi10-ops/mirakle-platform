# extensions.py
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")

login_manager.login_view = 'auth.login'
login_manager.login_message = None
login_manager.login_message_category = "info"
