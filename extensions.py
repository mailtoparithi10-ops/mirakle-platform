# extensions.py
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()

# Rate limiter configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

login_manager.login_view = 'auth.login'
login_manager.login_message = None
login_manager.login_message_category = "info"
