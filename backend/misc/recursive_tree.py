from src.extentions import db
from ..users.models import User
from ..bookmarks.models import Bookmark
from flask_login import current_user
import datetime
from sqlalchemy import literal
from sqlalchemy.orm import joinedload
from urllib.parse import urlparse


# generater
# リスト化してrootでコミットが早い？
def of_json(node, parent_id):
    time = None
    if node.get('add_date'):
        time = datetime.datetime.fromtimestamp(float(node.get('add_date')))

    if node.get("type") == "bookmark":
        bookmark = {
            "type": 1,
            "title": node.get('title'),
            "url": node.get('url'),
            "icon": node.get('icon'),
            "created_at": time,
            "parent_id": parent_id,
            "owner_id": current_user.id,
        }
        db.session.add(Bookmark(**bookmark))
        db.session.commit()
        return

    elif node.get("type") == "folder":
        bookmark_a = {
            "type": 0,
            "title": node.get('title'),
            "created_at": time,
            "parent_id": parent_id,
            "owner_id": current_user.id
        }
        bookmark = Bookmark(**bookmark_a)
        db.session.add(bookmark)
        db.session.commit()
        for child in node.get('children'):
            of_json(child, bookmark.id)
        return


# with unique restriction
def of_json2(node, parent_id):
    time = None
    if node.get('add_date'):
        time = datetime.datetime.fromtimestamp(float(node.get('add_date')))
        # time = datetime.datetime.fromtimestamp(int(node.get('add_date')))
        # time = datetime.datetime.fromtimestamp(node.get('add_date'))

    if node.get("type") == "bookmark":
        bookmark = {
            "type": 1,
            "url": node.get('url'),
            "owner_id": current_user.id,
        }
        q = db.session.query(Bookmark).filter_by(**bookmark)
        if db.session.query(literal(True)).filter(q.exists()).scalar():
            return

        # if db.session.query(literal(True)).filter(Bookmark.--- == ---).first():
        # if db.session.query(Bookmark).filter_by(**bookmark).first():
        #     return
        # either http or https...
        # icon
        # validate

        bookmark.update({
            "title": node.get('title'),
            "icon": node.get('icon'),
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
                "title": node.get('title'),
                "created_at": time,
                "owner_id": current_user.id
            }
        else:
            # for safari
            bookmark_a = {
                "type": 0,
                "title": node.get('title'),
                "owner_id": current_user.id
            }
            
        # 意味ある？
        t = db.session.query(Bookmark).filter_by(**bookmark_a).limit(1).first()
        if t:
            for child in node.get('children'):
                of_json2(child, t.id)
            return
        else:    
            bookmark_a.update({"parent_id": parent_id})
            bookmark = Bookmark(**bookmark_a)
            db.session.add(bookmark)
            db.session.commit()
            for child in node.get('children'):
                of_json2(child, bookmark.id)
            return


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
