from flask import Flask, jsonify
from src.config import Config
import logging

from src.extentions import cors, mail, login_manager, auth_required, migrate, db, celery
from src.extentions import ensure_signup_store, user_store
from src.extentions import mongo
import src.bookmarks.views
import src.users.views
import src.auth.views

from src.users.models import User

from flask import send_file, render_template
import os


def init_extensions(app):
    cors.init_app(app, 
                #   resources=r'/api/*',
                  resources=r'/*',
                  origins=app.config.get('CORS_ORIGINS'),
                  allow_headers=app.config.get('CORS_ALLOW_HEADERS'),
                  supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS')
                 )
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    mongo.init_app(app)

def create_app():
    app = Flask(__name__, template_folder='dist', static_folder='dist/static')
    app.config.from_object(Config)
    logging.basicConfig(level=logging.INFO)
    init_extensions(app)
    
    app.register_blueprint(src.bookmarks.views.blueprint, url_prefix='/api/v1/bookmarks')
    app.register_blueprint(src.users.views.blueprint, url_prefix='/api/v1/users')
    app.register_blueprint(src.auth.views.blueprint, url_prefix='/api/v1/auth')
    
    return app

def make_celery(app):
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery




app = create_app()
celery = make_celery(app)
ensure_signup_store.ping()
user_store.ping()


@login_manager.user_loader
def user_loader(id):
    return db.session.query(User).filter_by(id=id).one()

@login_manager.unauthorized_handler
def unauthorized():
    return {'message': 'Login is required.'}, 401

@app.errorhandler(422)
def page_not_found(error):
    return {'message': error.data.get('messages', error)}, 422


if app.config.get('ENV') == 'development':
    @app.route('/static/images/favicon/<name>')
    def favicon(name):
        if os.path.isfile(static_file('favicon', name)):
            return send_file(static_file('favicon', name), mimetype='image/png')
        else:
            # @fix: ここで，taskに探索させにいくべき．icon自体がない場合，とりあえずMを設定してしまう．
            return send_file(os.path.join('static','missing.png'), mimetype='image/png', cache_timeout=10)


    # @fix add-hoc
    # from flask_cors import cross_origin
    # @cross_origin() https://flask-cors.readthedocs.io/en/latest/
    @app.route('/static/images/usericon/<name>')
    def usericon(name):
        if os.path.isfile(static_file('usericon', name)):
            return send_file(static_file('usericon', name), mimetype='image/png', cache_timeout=5)
        else:
            return send_file(os.path.join('static','missing.png'), mimetype='image/png', cache_timeout=10)

    @app.route('/', methods=["GET"])
    def serve():
        return render_template('index.html')

    @app.route('/<path:some>', methods=["GET"])
    def serve2(some):
        return render_template('index.html')

    def static_file(type, id):
        file = os.path.join(os.path.dirname(__file__), 'static', 'images', type, id)
        return file
