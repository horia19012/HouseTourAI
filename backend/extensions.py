from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
bcrypt = Bcrypt()
jwt = JWTManager()
