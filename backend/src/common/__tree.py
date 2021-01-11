from flask_login import current_user
from src.extentions import db

from ..users.models import User
from ..bookmarks.models import Bookmark
from ..bookmarks.serializers import bookmark_schema_for_title_and_url

import datetime
from sqlalchemy import literal
from sqlalchemy.orm import joinedload

from flask import current_app
import src.common.tasks as tasks
import os
from urllib.parse import urlparse, urlunparse, urljoin

# depth-first traverse
# f: v' -> unit
# it seems nonsence bacause of using stack
def dft(f, r, init=None):
    s = [(r, init)]
    while (len(s) > 0):
        (n, p_id) = s.pop()
        id = f(n, p_id)
        if (n.get('children')):
            # for child in reversed(n.get('children')):
            for child in n.get('children'):
                s.append((child, id))

# リスト化してrootでコミットが早い？
# userが実行時に決定される？
def raw_of_json(node, parent_id):
    time = None
    if node.get('add_date'):
        time = datetime.datetime.fromtimestamp(float(node.get('add_date')))

    if node.get("type") == "bookmark":
        bookmark = {
            "type": 1,
            "title": None,
            "url": None,
            "created_at": time,
            "parent_id": parent_id,
            "owner_id": current_user.id,
        }
        bookmark.update(bookmark_schema_for_title_and_url.load(node))

        # either http or https...？
        (scheme, netloc, *_) = urlparse(node.get('url'))
        # @fix direct ref
        filename = os.path.join(current_app.config['APP_DIR'], 'static', 'images', 'favicon', netloc + '.png')
        tasks.saveFavicon.delay(urlunparse((scheme, netloc, '/', '','','')), filename)

        db.session.add(Bookmark(**bookmark))
        db.session.commit()
        return None

    elif node.get("type") == "folder":
        bookmark_a = {
            "type": 0,
            "title": None,
            "created_at": time,
            "parent_id": parent_id,
            "owner_id": current_user.id
        }
        bookmark_a.update(bookmark_schema_for_title_and_url.load(node))
        
        bookmark = Bookmark(**bookmark_a)
        db.session.add(bookmark)
        db.session.commit()
        return bookmark.id


# with unique restriction
def raw_of_json2(node, parent_id):
    time = None
    if node.get('add_date'):
        time = datetime.datetime.fromtimestamp(float(node.get('add_date')))

    if node.get("type") == "bookmark":
        bookmark = {
            "type": 1,
            "title": None,
            "url": None,
            "owner_id": current_user.id,
        }
        # @fix title is needed?
        bookmark.update(bookmark_schema_for_title_and_url.load(node))

        q = db.session.query(Bookmark).filter_by(**bookmark)
        if db.session.query(literal(True)).filter(q.exists()).scalar():
            return

        # @fix either http or https...？
        (scheme, netloc, *_) = urlparse(node.get('url'))
        # @fix direct ref
        filename = os.path.join(current_app.config['APP_DIR'], 'static', 'images', 'favicon', netloc + '.png')
        tasks.saveFavicon.delay(urlunparse((scheme, netloc, '/', '','','')), filename)
            
        bookmark.update({
            "created_at": time,
            "parent_id": parent_id,
            "owner_id": current_user.id,
        })
        db.session.add(Bookmark(**bookmark))
        db.session.commit()
        return

    elif node.get("type") == "folder":
        if time:
            bookmark_a = {
                "type": 0,
                "title": None,
                "created_at": time,
                "owner_id": current_user.id
            }
        else:
            # for safari
            bookmark_a = {
                "type": 0,
                "title": None,
                "owner_id": current_user.id
            }
        
        bookmark_a.update(bookmark_schema_for_title_and_url.load(node))
        t = db.session.query(Bookmark).filter_by(**bookmark_a).first()
        if t:
            return t.id
        else:    
            bookmark_a.update({"parent_id": parent_id})
            bookmark = Bookmark(**bookmark_a)
            db.session.add(bookmark)
            db.session.commit()
            return bookmark.id

# generater
def of_json(node, parent_id):
    dft(raw_of_json, node, init=parent_id)

def of_json2(node, parent_id):
    dft(raw_of_json2, node, init=parent_id)


def to_tree(node, targets):
    rest = []
    for target in targets:
        if target['parent_id'] == node['id']:
            node['children'].append({
                    'id': target['id'],
                    'type': target['type'],
                    'title': target['title'],
                    'children': []
            })
        else:
            rest.append(target)
    if len(rest) > 0:
        for child in node['children']:
            to_tree(child, rest)


# misc.
def search_bookmarks_raw(queries, node, result):
    for child in node.children:
        if child.type == 1:
            if search_or(queries, child.title):
                result.append(child)
        elif child.type == 0:
            if search_or(queries, child.title):
                result.append(child)
            search_bookmarks_raw(queries, child, result)


def search_or(search_words, target_string):
    return any(word.lower() in target_string.lower() for word in search_words)


# include itself
def isChild(sub_root, node):
    t = db.session.query(Bookmark).options(joinedload('parent')).filter_by(id=node).one()
    root_id = t.owner.root_id
    while True:
        if t.id == sub_root:
            return True
        elif t.id == root_id:
            return False
        t = t.parent
