from flask import Blueprint, jsonify, request, make_response, session
from flask_login import logout_user, current_user
from flask_apispec import use_kwargs

from src.extentions import auth_required, db, ensure_signup_store, mongo
from bson.objectid import ObjectId

import base64
from ..users.models import User
from ..users.serializers import user_schema
import os

blueprint = Blueprint('users', __name__)


@blueprint.route('', methods=['GET'])
def rootid_by_username():
    username = request.args.get('username') 
    user_a = db.session.query(User).filter_by(username=username).first()
    if user_a:
      # @fix 全部返しておk　あくまで疎なapi鯖として実装．
      return {
          'root_id': user_a.root_id,
          'name': user_a.name
      }, 200
    else:
      return {'message': 'There is no such a user.'}, 400


@blueprint.route('', methods=['PUT'])
@auth_required
@use_kwargs(user_schema, location='json')
def basic_update(name, **kwargs):
  current_user.name = name
  db.session.commit()

  usericon = kwargs.get('usericon')
  if usericon:
    data = usericon.split(',', 1)[1]
    plain_data = base64.b64decode(data)
    # @fix @check direct ref
    with open(os.path.join('src', 'static', 'images', 'usericon', current_user.username + '.png'), 'wb') as fp:
        fp.write(plain_data)
    return {'message': "Changed your name and usericon"}, 200

  return {'message': "Changed your name"}, 200


# @fix need some confirmation
@blueprint.route('/email', methods=['PATCH'])
@auth_required
@use_kwargs(user_schema, location='json')
def update_for_email(email, password):
  # @ fix verbose get of first()
  if current_user.check_password(password) and not ensure_signup_store.get(email) and not db.session.query(User).filter(User.email == email).first():
    current_user.email = email
    db.session.commit()
    return {'message': "Changed your email"}, 200

  return {'message': "The email address and/or password is invaild."}, 400

@blueprint.route('/password', methods=['PATCH'])
@auth_required
@use_kwargs(user_schema, location='json')
def update_for_password(new_password, password):
  if current_user.check_password(password):
    current_user.set_password(new_password)
    db.session.commit()
    return {'message': "Changed your password"}, 200

  return {'message': "The password is invaild."}, 400


@blueprint.route('/delete', methods=['POST'])
@auth_required
@use_kwargs(user_schema, location='json')
def delete(password):
  if current_user.check_password(password):
    # @fix ad hoc, doesn't work
    # db.session.delete(current_user) 
    db.session.query(User).filter_by(id=current_user.id).delete()
    db.session.commit()
    mongo.db.bookmarks.delete_many({"owner_id": current_user.id})

    logout_user()
    out = jsonify({"message": "Delete your account"})
    del session['csrf_token']
    return make_response(out, 200)

  return {'message': "The password is invaild."}, 400
