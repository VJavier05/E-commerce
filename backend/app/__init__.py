from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import os
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config

# Get configuration based on environment
config_name = os.environ.get('FLASK_ENV') or 'development'
app_config = config.get(config_name, config['default'])

app = Flask(__name__)
app.config.from_object(app_config)

# Initialize CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Upload folder configurations
app.config['REVIEW_UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/review_images')
app.config['UPLOAD_CHAT_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


db = SQLAlchemy(app)
mail = Mail(app) 

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)
jwt = JWTManager(app)



# DEBUGGING ROUTES (EMERGENCY)
# @app.before_request
# def list_routes():
#     for rule in app.url_map.iter_rules():
#         print(f"Route: {rule} | Methods: {list(rule.methods)}")


from app import routes
