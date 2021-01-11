from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from flask import abort
# mongoを与えて作成するモジュールとして扱うべきか．
# DB interface for editing bm
'''
user, bm for access to DB

for each functions,
    user_id, parameters such as target and distination.
'''

# generater
# 送り主がrootを持っていないときだけ，rootを設定してやればいいと思う
# parent ref
def of_json(mongo, root, parent):
    db = mongo.db.bookmarks
    if root.get("type") == "bookmark":
        # isLeafに変えた方が無難？
        db.insert_one({
            "type": "bookmark",
            "title": root["title"],
            "url": root["url"],
            "icon": root.get("icon"),
            "parent": parent
        })
        return
    elif root.get("type") == "folder":
        parent1 = db.insert_one({
            "type": "folder",
            "title": root["title"],
            "parent": parent
        }).inserted_id
        for node in root.get("children"):
            if node:
                of_json(mongo, node, parent1)
    else:
        abort(404) # bad interface

# DuplicateKeyError
def makeRoot(mongo):
    node = mongo.db.bookmarks.insert_one({
        "type": "folder",
        "title": "Root",
        "parent": None
    }).inserted_id
    return node

# transformer
# new file, title
def addNode(mongo, title, dist):
    mongo.db.bookmarks.insert_one({"title": title, "type": "folder", "parent": ObjectId(dist)})
    
# 一応idで送ってきて欲しい，すると単にobjectIdで囲むだけ．
def moveNode(mongo, src, dist):
    # loads? objectId?
    mongo.db.bookmarks.update_one({"_id": loads(src)}, {"$set": {"parent": loads(dist)}})

def withoutLeaf(mongo, node, result):
    db = mongo.db.bookmarks
    def withoutLeaf_raw(node):
        for child in db.find({"parent": node}):
            if child.type == "folder":
                result.append(child)
                withoutLeaf_raw(child._id)
    withoutLeaf_raw(node)
                
# 自分自身と，そいつを親に持つ子供も消去する
def removeNode(mongo, src):
    db = mongo.db.bookmarks
    id = ObjectId(src)
    t = db.find_one_and_delete({"_id": id})
    if t["type"] == "folder":
        for n in db.find({"parent": id}):
            removeNode(mongo, str(n["_id"]))
 No newline at end of file
