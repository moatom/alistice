from flask_cors import CORS
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import redis

from flask_login import login_required
from functools import wraps
from flask import request, session
from itsdangerous import URLSafeSerializer, BadSignature

from src.config import Config
from celery import Celery


cors = CORS()
mail = Mail()
mongo = PyMongo()
login_manager = LoginManager()
migrate = Migrate()
db = SQLAlchemy()
ensure_signup_store = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
user_store = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
celery = Celery(
        __name__,
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL,
        include=['src.common.tasks']
        )
signer = URLSafeSerializer(Config.ITSDANGEROUS_KEY)

def auth_required(f):
    @wraps(f)
    @login_required
    def wrap(*arg, **kwargs):
        # print('=========',session,'=========')
        # print('=========',request.headers,'=========')
        # for loss of response
        request.get_json()
        try:
            #  # it seems not valid because session start is vulnerable to CSRF
            if session.get("csrf_token") and request.headers.get('X-Csrf-Token'):
                if signer.loads(session.get("csrf_token"), salt='csrf-token-salt') ==\
                   request.headers.get('X-Csrf-Token'):
                    return f(*arg, **kwargs)
                return {'message': 'CSRF token is wrong.'}, 401
            return {'message': 'CSRF token is missing.'}, 401
        except (BadSignature, ValueError):
            return {'message': 'Invalid CSRF token'}, 401
    return wrap