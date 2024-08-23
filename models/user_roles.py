from db import db

class UsersRoles(db.Model):
    __tablename__ = "users_roles"

    user_roles_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    roles_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"))