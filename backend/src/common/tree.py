from flask_login import current_user

from src.extentions import mongo
from bson.objectid import ObjectId
from bson.json_util import dumps, loads

from ..users.models import User
from ..bookmarks.serializers import bookmark_schema_for_title_and_url, bookmark_schema
import datetime


from flask import current_app
import src.common.tasks as tasks
import os
from urllib.parse import urlparse, urlunparse, urljoin

from collections import deque

# utils
# @fix aggregate to an obj
# gn -> tr -> cn
def gn_from_root_to(node: 'ObjectId'):
  '''
  - include itself in ascending order of depth (i.e. from root to node)
  - length of returned value - 1 is depth of a node
  '''
  t = list(mongo.db.bookmarks.aggregate([
                {    
                  "$graphLookup": {       
                  "from": "bookmarks",       
                  "startWith": node,       
                  "connectFromField": "parent_id",
                  "connectToField": "_id",
                  "depthField": "reversed_depth",
                  "as": "parents" }
                },
                {
                  "$match": { "_id": node }
                },
                # { "$project": { "parents": 1 } },a
                ]))
  return sorted(t[0]['parents'], key=lambda e: -e['reversed_depth']) if len(t) == 1 else []


def tr_parents_id(source):
  '''
  - up to 10 query is published
  - just need _ids
  # t = mongo.db.bookmarks.find_one("_id": node)
  # parents = []
  # while t['parent_id']:
  #   t = mongo.db.bookmarks.find_one("_id": t['parent_id'])
  #   parents.append(str(t['_id']))
  # return parents
  '''
  # @fix is it generotor?
  # @opt 
  t = list(map(lambda e: str(e["_id"]), source))
  return t[:len(t)-1]


def cn_depth(source):
  # @fix else's depth
  return -source[0]['reversed_depth'] if len(source) > 0 else 10000


def cn_routes(source):
  return list(map(lambda e: {"id": str(e["_id"]),
                             "title": e["title"]},
                  source))

def gn_tree():
  '''
  # for mongo shell
  db.bookmarks.aggregate([
    { $match: {
        parent_id: null,
        owner_id: 1
    }},
    { $graphLookup: {
        from: "bookmarks",
        startWith: "$_id",
        connectFromField: "_id",
        connectToField: "parent_id",
        depthField: "depth",
        as: "children"
    }}
  ])
  '''
  t = mongo.db.bookmarks.aggregate([
    { "$match": {
        "_id": ObjectId(current_user.root_id)
    }},
    { "$graphLookup": {
        "from": "bookmarks",
        "startWith": "$_id",
        "connectFromField": "_id",
        "connectToField": "parent_id",
        "depthField": "depth",
        "as": "children"
    }}
  ])
  t = list(t)
  return t[0] if len(t) == 1 else None

def gn_tree_without_leaf():
  t = mongo.db.bookmarks.aggregate([
    { "$match": {
        "_id": ObjectId(current_user.root_id),
        # "parent_id": None,
        # "type": 0,
        # "owner_id": current_user.id
    }},
    { "$graphLookup": {
        "from": "bookmarks",
        "startWith": "$_id",
        "connectFromField": "_id",
        "connectToField": "parent_id",
        "depthField": "depth",
        "as": "children",
        # "restrictSearchWithMatch": { "depth": {"$lte": 5},
        #                              "type": 0 }
        # "maxDepth": 5
    }}
  ])
  t = list(t)
  return t[0] if len(t) == 1 else None

# ------------------------------
def regularlize_bookmark(bookmark, unique):
  '''
    regularlization in the whole of database
  '''
  time = datetime.datetime.fromtimestamp(float(bookmark.get('add_date')), datetime.timezone.utc) if bookmark.get('add_date') else datetime.datetime.now(datetime.timezone.utc)
  if unique:
    # @fix title is needed?
    _bookmark = {
      "type": 1,
      "title": None,
      "url": None,
      "owner_id": current_user.id,
    }
    _bookmark.update(bookmark_schema_for_title_and_url.load(bookmark))
    # @opt
    if mongo.db.bookmarks.find_one(_bookmark):
      raise ValueError

    _bookmark.update({
        "created_at": time,
        "parent_id": bookmark["parent_id"]
    })
    return _bookmark

  else:
    _bookmark = {
        "type": 1,
        "title": None,
        "url": None,
        "owner_id": current_user.id,
        "created_at": time,
        "parent_id":bookmark["parent_id"]
    }
    _bookmark.update(bookmark_schema_for_title_and_url.load(bookmark))
    return _bookmark



def regularlize_folder(folder, unique):
  '''
    regularlization in the whole of database
  '''
  time = datetime.datetime.fromtimestamp(float(folder.get('add_date')), datetime.timezone.utc) if folder.get('add_date') else datetime.datetime.now(datetime.timezone.utc)
  if unique:
    if time:
      _folder = { "type": 0,
                  "title": None,
                  "created_at": time,
                  "owner_id": current_user.id }
    else: # for safari
      _folder = { "type": 0,
                  "title": None,
                  "owner_id": current_user.id }
    
    _folder.update(bookmark_schema_for_title_and_url.load(folder))
    t = mongo.db.bookmarks.find_one(_folder)
    if t:
      raise ValueError((
                        t["id"],
                        t["depth"]
                      ))
    else:    
      _folder.update({
                      "parent_id": folder["parent_id"]
                     })
      return _folder

  else:
    _folder = { 
                "type": 0,
                "title": None,
                "created_at": time,
                "owner_id": current_user.id,
                "parent_id": folder["parent_id"]
              }
    _folder.update(bookmark_schema_for_title_and_url.load(folder))
    return _folder


def add_bookmark(bookmark, unique):
  try:
    _bookmark = regularlize_bookmark(bookmark, unique)
    mongo.db.bookmarks.insert_one(_bookmark)
    # either http or https...？
    (scheme, netloc, *_) = urlparse(_bookmark['url'])
    # @fix direct ref
    filename = os.path.join(current_app.config['APP_DIR'], 'static', 'images', 'favicon', netloc + '.png')
    tasks.saveFavicon.delay(urlunparse((scheme, netloc, '/', '','','')), filename)
  except ValueError:
    return


def add_folder(folder, unique, depth):
  '''
  if a folder is duplicated, original one's depth is used.
  '''
  try:
    _folder = regularlize_folder(folder, unique)
    parent_id = mongo.db.bookmarks.insert_one(_folder).inserted_id
  except ValueError as e:
    parent_id, depth = e.args

  if folder.get("children"):
    for child in folder.get("children"):
      of_json(child, parent_id, depth+1, unique)


def search_and(search_words, target_string):
  return all(word.lower() in target_string.lower() for word in search_words)

def search_or(search_words, target_string):
  return any(word.lower() in target_string.lower() for word in search_words)

import re
import urllib.parse
def search_or_url(search_words, target_url):
  '''
  filter(lambda e: e, re.split(r'(?:%\w\w)+|[ -/:-@\[-`{-~]', "https://off.tokyo/blog/python%E3%81%A7%E6%96%87%E5%AD%97%E5%88%97%E3%81%8B%E3%82%89%E8%8B%B1%E5%8D%98%E8%AA%9E%E3%82%92%E6%8A%9C%E3%81%8D%E5%87%BA%E3%81%97%E9%9B%86%E8%A8%88%E3%81%99%E3%82%8B/"))
  filter(lambda e: e, re.split(r'(?:%\w\w)+|[ -/:-@\[-`{-~]', "https://docs.python.org/ja/3/library/re.html#re.split"))
  '''
  targets = filter(lambda e: e, re.split(r'(?:%\w\w)+|[ -/:-@\[-`{-~]', urllib.parse.unquote(target_url)))
  for target in targets:
    if search_or(search_words, target):
      return True
  return False

def search_in_tree(queries, user):
  '''
  it has side effect on lists
  '''
  all=[]
  any=[]

  for node in mongo.db.bookmarks.find({"_id": {"$ne": ObjectId(user.root_id)},
                                        "owner_id": user.id}):
    if node['type'] == 1:
      if search_and(queries, node['title']):
        all.append(node)
      elif search_or(queries, node['title']) or search_or_url(queries, node['url']):
        any.append(node)

    elif node['type'] == 0:
      if search_and(queries, node['title']):
        all.append(node)
      elif search_or(queries, node['title']):
        any.append(node)

  return all + any




# input
def of_json(node, parent_id: 'ObjectId', depth=1, unique=False):
  '''
  root's depth is 0
  ---- this might be better (fusion is required)
  def of_json(node):
    return raw_of_json([node])

  # breadth first
  @tail_recursive
  def raw_of_json(nodes):
    if not nodes:
      return
    else:
      next_nodes = []
      for node in nodes:
        process node (if node.type == 0: ... else ... )
        next_nodes.append(*node.children)
      return raw_of_json(next_nodes.node)
  '''
  if depth > 5:
    # @fix it should be error
    return

  node["parent_id"] = parent_id
  if node.get("type") == "bookmark":
    return add_bookmark(node, unique)
  elif node.get("type") == "folder":
    return add_folder(node, unique, depth)


# output
def to_tree(node, targets, depth=1):
  if depth > 5:
    return

  rest = []
  for target in targets:
      if str(target['parent_id']) == node['id']:
        # @opt created_at is no need
        _target = bookmark_schema.dump(target)
        _target['children'] = []
        node['children'].append(_target)
      else:
          rest.append(target)

  if len(rest) > 0:
      for child in node['children']:
          to_tree(child, rest, depth+1)




def removeNodes(src: str):
  '''
  Remove a subtree rooted by src
  rawRemoveNodes(ObjectId(src))
  '''
  q = deque()
  q.append(ObjectId(src))
  while q:
    id = q.popleft()
    t = mongo.db.bookmarks.find_one_and_delete({"_id": id, "owner_id": current_user.id})
    if t and t["type"] == 0:
      for n in mongo.db.bookmarks.find({"parent_id": id, "owner_id": current_user.id}):
        q.append(n["_id"])



# # DuplicateKeyError
# def makeRoot(mongo):
#     node = mongo.db.bookmarks.insert_one({
#         "type": "folder",
#         "title": "Root",
#         "parent": None
#     }).inserted_id
#     return node

# # transformer
# def withoutLeaf(mongo, node, result):
#     db = mongo.db.bookmarks
#     def withoutLeaf_raw(node):
#         for child in db.find({"parent": node}):
#             if child.type == "folder":
#                 result.append(child)
#                 withoutLeaf_raw(child._id)
#     withoutLeaf_raw(node)
 
# def rawRemoveNodes(id: 'ObjectId'):
#   '''
#   Remove a subtree rooted by id
#   '''
#   t = mongo.db.bookmarks.find_one_and_delete({"_id": id, "owner_id": current_user.id})
#   if t["type"] == 0:
#     for n in mongo.db.bookmarks.find({"parent_id": id, "owner_id": current_user.id}):
#       rawRemoveNodes(n["_id"])