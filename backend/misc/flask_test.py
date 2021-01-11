from marshmallow import Schema, fields, validate, ValidationError


class BookmarkSchema(Schema):
    id = fields.Integer()
    type = fields.Integer(required=True, validate=validate.OneOf([0, 1]))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    url = fields.Url(required=True, validate=validate.Length(max=2048))
    created_at = fields.DateTime(dump_only=True)
    parent_id = fields.Integer()
    owner_id = fields.Integer()


bookmark_schema = BookmarkSchema()
bookmarks_schema = BookmarkSchema(many=True)


a = BookmarkSchema().\
    load({'type': 1, 'title': '', 'url': 'http://foo.com/aaa', 'aaa': 'q'})

print(a)