# extensions.py
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

login_manager.login_view = 'auth.login'
