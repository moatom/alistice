from flask import Blueprint, request, jsonify
from ..common.tree import of_json, addNode, moveNode, removeNode, makeRoot, withoutLeaf
from src.extentions import auth_required, mongo
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask_login import current_user

blueprint = Blueprint('bookmarks', __name__)

@blueprint.route('/add', methods=['POST'])
@auth_required
def add_bookmarks():
    # user_id = user["_id"]
    bm = request.get_json()
    # print("bm", bm)
    if not bm:
        return jsonify("invalid"), 400
    user = mongo.db.users.find_one({"email": current_user.email})
    # eroor handling is needed？
    for src in bm.get("children"):
        # should raise an eroor
        of_json(mongo, src, user.get("root"))
    return jsonify({"message": "Success"}), 200
    # return dumps({"root": mongo.db.bookmarks.find_one({"parent": user_id})}), 200
    # return jsonify("invalid"), 400


@blueprint.route('/get', methods=['GET'])
def get_bookmarks():
    db = mongo.db.bookmarks
    pwd = request.args.get('pwd')  # もしかしたら，get_listかも 現在のdirの
    tree = pwd.split("/")
    # クライアント側で，splitされたpwdと一緒に走査する
    title_path = []
    for e in tree:
        t = db.find_one({"_id": ObjectId(e)})
        if t:
            title_path.append(t)
    # this is the titles for a good display.
    return dumps({
        "title_path": map(lambda e: e["title"], title_path),
        "children": db.find({"parent": ObjectId(tree[-1])})
    }), 200

@blueprint.route('/move', methods=['GET','POST'])
@auth_required
def move_bookmarks():
    if request.method == 'GET':
        # return folder tree for selection
        result = []
        withoutLeaf(mongo, current_user.root, result)
        return jsonify(result), 200

# those should be id list of sub trees' roots
    srcs = request.get_json()['srcs']
    dist = request.get_json()['dist']
    for src in srcs:
        moveNode(mongo, src, dist)
    return jsonify({"message": "Success"}), 200

# 自分のbookmarkへの操作かを確認する必要があるかも・・・
@blueprint.route('/delete', methods=['POST'])
@auth_required
def delete_bookmarks():
    srcs = request.get_json()['srcs']
    for src in srcs:
        removeNode(mongo, src)
    return jsonify({"message": "Success"}), 200

# http://infra.hatenablog.com/entry/2014/01/27/224342
# db.find({"parent": current_user.id,
#          "$text": {"$search": queries}})
@blueprint.route('/search', methods=['GET'])
@auth_required
def search_bookmarks():
    queries = request.args.get('q').split()
    print(queries)
    if not queries:
        return jsonify({"message": "Not matched"}), 400

    db = mongo.db.bookmarks
    result = []
    # print("queries:", queries, "\n\n\n")
    def search_bookmarks_raw(node, result):
        children = db.find({"parent": node})
        for child in children:
            if child.get("type") == "bookmark":
                if search_or(queries, child.get("title")):
                    result.append(child)
            elif child.get("type") == "folder":
                if search_or(queries, child.get("title")):
                    result.append(child)
                search_bookmarks_raw(child.get("_id"), result)
    search_bookmarks_raw(current_user.root, result)
    if not result:
        return jsonify({"message": "Not matched"}), 400
    return dumps({"result": result}), 200

def search_or(search_words, target_string):
    return any(word.lower() in target_string.lower() for word in search_words)

# そんなに遅くはないので，とりあえずならありかも？埋め込んだ方が早いけど．．．
def check_root(node):
    db = mongo.db.bookmarks
    node = db.find_one({"_id": node.parent})
    while node.parent:
        node = db.find_one({"_id": node.parent})
    return current_user.root == node._id