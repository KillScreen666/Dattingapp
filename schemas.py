from marshmallow import Schema, fields

class PlainAccountSchema(Schema):
    account_id = fields.Int(dump_only=True)
    active = fields.Bool(required=True)

class PlainUserSchema(Schema):
    user_id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    # load_only on passwords! IMPORTANT: never return the password to the user
    password = fields.Str(required=True, load_only=True) 
    email = fields.Str(required=True)

class AccountSchema(PlainAccountSchema):
    users = fields.List(fields.Nested(PlainUserSchema()), dump_only=True)


class UserUpdateSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Str(required=True, unique=True)


class PlainRoleSchema(Schema):
    role_id = fields.Int(dump_only=True)
    role_name = fields.Str(required=True)

class RoleSchema(PlainRoleSchema):
    users = fields.List(fields.Nested(PlainUserSchema()), dump_only=True)


class RoleUpdateSchema(Schema):
    role_name = fields.Str(required=True)

class UserSchema(PlainUserSchema):
    account_id = fields.Int(required=True, load_only=True)
    account = fields.Nested(PlainAccountSchema(), dump_only=True)
    
    roles = fields.List(fields.Nested(PlainRoleSchema()), dump_only="True")

class RoleAndUserSchema(Schema):
    user = fields.Nested(UserSchema)
    role = fields.Nested(RoleSchema)

class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)