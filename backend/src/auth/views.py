from flask import Blueprint, request, jsonify, redirect, url_for, current_app, session
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from src.extentions import auth_required, db, mongo

from src.extentions import ensure_signup_store, user_store, signer, mail
from ..users.models import User
from ..users.serializers import user_schema

from bson.json_util import dumps
from json import loads
from werkzeug.security import generate_password_hash, check_password_hash

import os
import re
from uuid import uuid4
import base64

from sqlalchemy import or_


# from flask_apispec import use_args,use_kwargs, marshal_with
from flask_apispec import use_kwargs


blueprint = Blueprint('auth', __name__)


@blueprint.route('/signup', methods=['POST'])
@use_kwargs(user_schema, location='json')
def signup(usericon, email, username, name, password):
    if ensure_signup_store.get(email) or ensure_signup_store.get(username) or\
       db.session.query(User).filter(or_(User.email == email, User.username == username)).first():
        return {'message': "The email adress and/or username is alread used."}, 400
    ensure_signup_store.set(email, 'true', current_app.config.get('STORE_EXPIRES'), nx=True)
    ensure_signup_store.set(username, 'true', current_app.config.get('STORE_EXPIRES'), nx=True)

    token = str(uuid4())
    # @fix at first, making user object
    user = {'usericon': usericon,
            'email': email,
            'username': username,
            'name': name,
            'password': generate_password_hash(password)}
    user_store.set(token, dumps(user), current_app.config.get('STORE_EXPIRES'), nx=True)
    
    # @fix email is not reflexed　MAIL_USERNAME　
    msg = Message(recipients=[email], sender=current_app.config.get('MAIL_USERNAME'), subject='Alistice: Activation')
    # @fix for url
    msg.html = ('Welcome to Alistice, ' + username + '.<br>' + \
                'We confirm you through <a href="{0}">{0}</a>.<br>' + \
                'This link is expired in 10 minutes.').format(f"{current_app.config.get('API_URL')}/auth/signin/mail/{token}")
    mail.send(msg)
    return '', 200

@blueprint.route('/signin/mail/<token>', methods=['GET'])
def mail_signin(token):
    t = user_store.get(token)
    if t:
        user_a = loads(t)
        data = user_a.get('usericon').split(',', 1)[1]
        plain_data = base64.b64decode(data)
        # @fix direct reference to a folder
        with open(f"./src/static/images/usericon/{user_a.get('username')}.png", 'wb') as fp:
            fp.write(plain_data)
        del user_a['usericon']

        # @fix need created_at
        bm_id = mongo.db.bookmarks.insert_one({'type': 0,
                                               'title': 'root'}).inserted_id
        user = User(**user_a, root_id=str(bm_id))
        db.session.add(user)
        db.session.commit()

        mongo.db.bookmarks.update_one({'_id': bm_id},
                                      {'$set': {'owner_id': user.id}})
        
        user_store.delete(token)
        login_user(user, remember=True)
        # @fix
        return redirect(url_for('serve'))
    return {'message': "Invalid link"}, 400

def signin_raw(email, password):
    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return {'message': "User is not found."}, 400
    if not check_password_hash(user.password, password):
        return {'message': "Password is incorrect."}, 400

    login_user(user, remember=True)
    # @fix output-shape
    return {"login": True,
            'username': user.username,
            'root_id': user.root_id}, 200
          
@blueprint.route('/signin', methods=['POST'])
def signin():
  if current_user.is_authenticated:
      return {
        "login": current_user.is_authenticated,
        "username": current_user.username,
        "root_id": current_user.root_id}, 200
  else:
    # user = {
    #     'email': None,
    #     'password': None
    # }
    # # @fix try-error
    # user.update(user_schema.load(request.get_json()))
    t = request.get_json()
    user = {
        'email': t.get('email'),
        'password': t.get('password')
    }
    return signin_raw(**user)

@blueprint.route('/signout', methods=['GET'])
# @login_required
def signout():
    logout_user()
    if current_user.is_authenticated and session.get('csrf_token'):
        del session['csrf_token']
    out = jsonify({"msg": "logged out"})
    return out, 200

@blueprint.route('/session/start', methods=["GET"])
@login_required
def session_start():
    t = str(uuid4())
    out = jsonify(csrf_token=t,
                  username=current_user.username,
                  root_id=current_user.root_id)
    # @check hashing needed? 
    session['csrf_token'] = signer.dumps(t, salt='csrf-token-salt')
    return out, 200