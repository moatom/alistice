from flask import Blueprint, request
from flask_apispec import use_kwargs
from flask_login import current_user, login_required
from ..common.tree import of_json, to_tree, search_in_tree, removeNodes
from ..common.tree import gn_from_root_to, tr_parents_id, cn_depth

from bson.objectid import ObjectId
from src.extentions import auth_required, db, mongo
from ..users.models import User
from ..bookmarks.serializers import bookmarks_schema, ShortBookmarkSchema1, ShortBookmarkSchema2
from datetime import datetime



blueprint = Blueprint('bookmarks', __name__)

DEPTH_LIMIT = 20
PER_PAGE = 100
LIMIT = 2000


# generate
# def raw_add_bookmarks(unique: bool, sub_root_id: str):
def raw_add_bookmarks(unique: bool):
    if mongo.db.bookmarks.count_documents({"owner_id": current_user.id}, limit=LIMIT) >= LIMIT:
        return {"message": f"The number of bookmaks is restricted up to about {LIMIT}."}, 400

    children = request.get_json().get("children")
    if children:
        for child in children:
            of_json(child, ObjectId(current_user.root_id), unique=unique)
        return '', 202

    return {"message": "invalid"}, 400


@blueprint.route('/add', methods=['POST'])
@auth_required
def add_bookmarks():
    return raw_add_bookmarks(False)


@blueprint.route('/uniqueadd', methods=['POST'])
@auth_required
def uniqueadd_bookmarks():
    return raw_add_bookmarks(True)

@blueprint.route('/title', methods=['PATCH'])
@auth_required
@use_kwargs(ShortBookmarkSchema1(), location='json')
def change_title(_id, title):
    if mongo.db.bookmarks.update_one({
        "_id": ObjectId(_id),
        "owner_id": current_user.id
        },
        {"$set": {"title": title}}
       ):
        return "", 200
    return {"message": "Not allowed edition"}, 400

@blueprint.route('/bookmark', methods=['PUT'])
@auth_required
@use_kwargs(ShortBookmarkSchema2(), location='json')
def add_file(title, parent_id):
    if mongo.db.bookmarks.find_one({
        "_id": ObjectId(parent_id),
        "owner_id": current_user.id
       }):
        add_bookmarks({
            "title": title
        })
        return "", 200
    return {"message": "Not allowed edition"}, 400




# result
# in children
@blueprint.route('/get', methods=['GET'])
def get_bookmarks():
    '''
    the head is root
    get for children
    '''
    id = ObjectId(request.args.get('q'))

    ids = []
    titles = []
    for e in gn_from_root_to(id) :
        ids.append(str(e['_id']))
        titles.append(e['title'])

    # @fix handle in list of object by gen_routes
    return {
        "ids": ids,
        "titles": titles,
        # @opt
        "children": bookmarks_schema.dump(mongo.db.bookmarks.find({"parent_id": id})),
    }, 200


# 分単位で規格化すると，キャッシュが可能
# curl "http://localhost:5000/api/bookmarks/latest?date=2020-03-06T23:24:52.780Z&page=1&username=moatom" -X GET -H "Content-Type: application/json"
@blueprint.route('/latest', methods=['GET'])
def latest_bookmarks():
    # fix serialize
    date = request.args['date']
    if date:
        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    page = int(request.args['page'])
    username = request.args['username']
    # @opt
    user = db.session.query(User).filter_by(username=username).first()
    if not user:
        return '', 200
        # return {"message": "There is no such a user."}, 400
    
    t = mongo.db.bookmarks.\
        find({"type": 1, "created_at": {"$lte": date}, "owner_id": user.id}).\
        sort([("created_at", -1)]).\
        skip(page * PER_PAGE).\
        limit(PER_PAGE)
    return {
        "children": bookmarks_schema.dump(t),
    }, 200


# search for logged in user
@blueprint.route('/search', methods=['GET'])
@auth_required
def search_bookmarks():
    # @fix キャッシュしておいて，そこからページングするべき
    # mongodbで直接サーチするべき．
    # up to 5 queries
    queries = request.args.get('q').split()[:5]
    if not queries:
        return {"message": "Not matched"}, 400
    # @fix twitter interface like from:moatom
    # user = db.session.query(User).filter_by(username=username).first()


    # @fix for more convenience
    result = search_in_tree(queries, current_user)
    if not result:
        return {"message": "Not matched"}, 400
    # @check dumping here is good?
    return {"result": bookmarks_schema.dump(result)}, 200


@blueprint.route('/export', methods=['GET'])
@auth_required
def export_bookmarks():
    '''
    done by toTree and some serialization.
    bookmarks_a = mongo.db.bookmarks.find({"_id": {"$ne": ObjectId(current_user.root_id)},
                                           "type": 0,
                                           "owner_id": current_user.id})
    bookmarks = bookmarks_schema.dump(bookmarks_a)
    root = {
        'id': current_user.root_id,
        # @check string? number?
        'type':  "folder",
        'title': 'root',
        'children': []
    }
    # map is not unit function
    _to_tree(root, map(lambda e: e['type']=concertType(e['type']), bookmarks))
    return {'root': root}, 200
    '''
    pass


# edit
@blueprint.route('/move', methods=['GET','POST'])
@auth_required
def move_bookmarks():
    if request.method == 'GET':
        bookmarks = mongo.db.bookmarks.find({"_id": {"$ne": ObjectId(current_user.root_id)},
                                             "type": 0,
                                             "owner_id": current_user.id,
                                            })
        root = {
            'id': current_user.root_id,
            'type':  0,
            'title': 'root',
            'children': []
        }
        to_tree(root, bookmarks)

        # @opt
        # # need to aply recursive validation for dump...
        # root = gn_tree_without_leaf()
        return {'root': root}, 200

    srcs = request.get_json()['srcs']
    dest = request.get_json()['dest']
    d = mongo.db.bookmarks.find_one({"_id": ObjectId(dest),
                                     "type": 0,
                                     "owner_id": current_user.id})
    root_id = str(current_user.root_id)

    if d:
        source = gn_from_root_to(d['_id'])
        if cn_depth(source) <= 5:
            parents_id = tr_parents_id(source)
            for src in srcs:
                if src != root_id and src != dest and not (src in parents_id):
                    mongo.db.bookmarks.update_one({
                                                   "_id": ObjectId(src),
                                                   "owner_id": current_user.id
                                                  },
                                                  {"$set": {"parent_id": d["_id"]}}
                                                 )
            return '', 200
    return {"message": "Not allowed edition"}, 400


# @fix rootは規制すべき．確認する．ただし，user消去のときは別．
@blueprint.route('/delete', methods=['POST'])
@auth_required
def delete_bookmarks():
    srcs = request.get_json()['srcs']
    root_id = str(current_user.root_id)
    for src in srcs:
        if src != root_id:
            removeNodes(src)
    return '', 200
