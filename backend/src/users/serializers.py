from marshmallow import Schema, fields, validate, validates, ValidationError

# https://marshmallow.readthedocs.io/en/stable/api_reference.html#marshmallow.fields.Dict
# https://github.com/marshmallow-code/marshmallow/blob/dev/src/marshmallow/validate.py#L355
class UserSchema(Schema):
    id = fields.Integer(load_only=True)
    email = fields.Email(validate=validate.Length(min=1, max=100), load_only=True)
    username = fields.String(validate=[validate.Length(min=1, max=15), validate.Regexp(r'^[A-Za-z0-9_]+$')])
    name = fields.String(validate=validate.Length(min=1, max=50))
    password = fields.Str(validate=[validate.Length(min=8, max=100), validate.Regexp(r'^[\x21-\x7e]+$')], load_only=True)# not hashed
    root_id = fields.Str()
    created_at = fields.DateTime('iso', dump_only=True)
    # none in db
    usericon = fields.String(load_only=True)
    # new_userで作ったら？
    new_password = fields.Str(validate=[validate.Length(min=8, max=100), validate.Regexp(r'^[\x21-\x7e]+$')], load_only=True)# not hashed

    @validates("usericon")
    def validate_usericon(self, usericon):
        if usericon.split(':', 1)[1].split(";", 1)[0] != 'image/png':
            raise ValidationError('Usericon must be PNG image.')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

# class ShortUserSchema(UserSchema):
#     class Meta:
#         fields = ['id', 'name']
