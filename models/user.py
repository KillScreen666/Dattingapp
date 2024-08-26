from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

    # 1 - many account has many users
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.account_id"), unique=False, nullable=False)
    account = db.relationship("AccountModel", back_populates="users")

    # many to many 
    roles = db.relationship("RoleModel", back_populates="users", secondary="users_roles")