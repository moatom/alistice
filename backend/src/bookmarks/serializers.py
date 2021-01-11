from marshmallow import Schema, fields, validate, ValidationError
import datetime as dt


class BookmarkSchemaForTitleAndUrl(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    url = fields.Url(validate=validate.Length(max=2048))

class BookmarkSchema(Schema):
    # id in JS / _id in Python loadすると，ObjectIdでなくなる．dumpも同様．
    _id = fields.Str(data_key="id")
    type = fields.Integer(required=True, validate=validate.OneOf([0, 1]))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # not required for folder
    url = fields.Url(validate=validate.Length(max=2048))
    # added when save to db
    created_at = fields.DateTime("iso", default=dt.datetime.now(dt.timezone.utc))
    parent_id = fields.Str(load_only=True)
    owner_id = fields.Integer(load_only=True)


# https://marshmallow.readthedocs.io/en/stable/quickstart.html#filtering-output
bookmark_schema = BookmarkSchema()
bookmarks_schema = BookmarkSchema(many=True)

bookmark_schema_for_title_and_url = BookmarkSchemaForTitleAndUrl(unknown='EXCLUDE')


class ShortBookmarkSchema1(BookmarkSchema):
    class Meta:
        fields = ['id', 'title']


class ShortBookmarkSchema2(BookmarkSchema):
    class Meta:
        fields = ['title', 'parent_id']
