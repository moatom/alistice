import os
from datetime import timedelta

class BaseConfig:
  # @fix random key is not good for development
  SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24).hex())
  ITSDANGEROUS_KEY = os.environ.get("ITSDANGEROUS_KEY", os.urandom(24).hex())
  APP_DIR = os.path.abspath(os.path.dirname(__file__))
  PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
  MAX_CONTENT_LENGTH = 5 * 1024 * 1024
  # flask-cors
  CORS_ORIGINS = ['http://localhost:80', 'http://127.0.0.1:80']
  # CORS_ORIGINS = ['http://localhost:80', 'http://127.0.0.1:80', 'http://localhost:3031', 'http://127.0.0.1:3031']
  CORS_ALLOW_HEADERS = ['Content-Type', 'X-Csrf-Token']
  CORS_SUPPORTS_CREDENTIALS = True
    # max_age=43200
  # flask-login
  # https://flask-login.readthedocs.io/en/latest/#cookie-settings
  # https://blog.miguelgrinberg.com/post/cookie-security-for-flask-applications
  SESSION_COOKIE_HTTPONLY = True
  REMEMBER_COOKIE_HTTPONLY = True
  REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True
  # flask-mail # https://myaccount.google.com/security
  MAIL_SERVER = 'smtp.gmail.com'
  MAIL_PORT = 465
  MAIL_USE_SSL = True
  MAIL_USERNAME = os.environ.get("MAIL_USERNAME") # need default settings for dev
  MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
  # Database
  STORE_EXPIRES = timedelta(minutes=10)
  CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
  CELERY_BROKER_URL = 'redis://localhost:6379/2'


if os.environ.get('FLASK_ENV') == 'production':
  class ProdConfig(BaseConfig):
    API_URL = 'https://alistice.com/api/v1'
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI')
    MONGO_URI = os.environ.get('PROD_MONGODB_URI')
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
  Config = ProdConfig

elif os.environ.get('FLASK_ENV') == 'staging':
  class StaConfig(BaseConfig):
    API_URL = 'http://localhost:80/api/v1'
    ENV = 'staging'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # @fix dangerous
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI')
    MONGO_URI = os.environ.get('PROD_MONGODB_URI')
    # # installig sql alchemy is required.
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SQLALCHEMY_ECHO=True
    # DB_NAME = 'dev.db'# need default user
    # DB_PATH = os.path.join(BaseConfig.PROJECT_ROOT, DB_NAME)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI', 'sqlite:///{0}'.format(DB_PATH))
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
  Config = StaConfig

elif os.environ.get('FLASK_ENV') == 'development':
  class DevConfig(BaseConfig):
    API_URL = 'http://localhost:5000/api/v1'
    ENV = 'development'
    DEBUG = True
    CORS_ORIGINS = ['http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:5000', 'http://127.0.0.1:5000']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO=True
    DB_NAME = 'local.db'# need default user
    DB_PATH = os.path.join(BaseConfig.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI', 'sqlite:///{0}'.format(DB_PATH))
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    MONGO_URI = 'mongodb://localhost:27017/test'
  Config = DevConfig
  from sqlalchemy import event
  from sqlalchemy.engine import Engine
  @event.listens_for(Engine, "connect")
  def set_sqlite_pragma(dbapi_connection, connection_record):
      cursor = dbapi_connection.cursor()
      cursor.execute("PRAGMA foreign_keys=ON")
      cursor.close()

else:
  raise Exception('no config')