import datetime
import os

from flask import Flask
from flask_cors import CORS
from huggingface_hub import login
from controllers.app_controller import app_controller
from extensions import (socketio, bcrypt, jwt)

from db import Base, engine

from websocket import register_socketio_handlers



app = Flask(__name__)

socketio.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
token = os.getenv("HUGGINGFACE_TOKEN")
if token:
    login(token=token)
else:
    print("Warning: No Hugging Face token found in environment.")

CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

UPLOAD_FOLDER = 'static/uploads'
GENERATED_VIDEOS_FOLDER = 'static/generated_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-secret')
expires_in = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '36000'))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=expires_in)

Base.metadata.create_all(bind=engine)
register_socketio_handlers(socketio)

app.register_blueprint(app_controller)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
