import os
import requests 


from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
from sqlalchemy import or_
from flask_jwt_extended import jwt_required
from passlib.hash import pbkdf2_sha256

# db config
from db import db
from models import UserModel
from schemas import UserSchema, UserUpdateSchema, UserRegisterSchema
# token block list
from blocklist import BLOCKLIST
# importing send email function
from tasks import send_user_registration_email

blp = Blueprint("User", "user", description="Operations on users")




@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        if UserModel.query.filter(
            or_(
                UserModel.username == user_data["username"]),
                UserModel.email == user_data["email"]
        ).first():
            abort(409, message="A user with that username or email already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            email=user_data["email"],
            # TODO create new or add to existing
            account_id=user_data["account_id"],
        )
        db.session.add(user)
        db.session.commit()

        current_app.queue.enqueue(send_user_registration_email, user.email, user.username)

        return {"message": "User created successfully."}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.email == user_data["email"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.user_id, fresh=True)
            refresh_token = create_refresh_token(user.user_id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # TODO add reddis here
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

@blp.route("/user")
class RoleList(MethodView):
    @blp.response(200, UserSchema(many=True))
    @jwt_required()
    def get(self):
        return UserModel.query.all() 

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @jwt_required(fresh=True)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User has been deleted."}

    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    @jwt_required(fresh=True)
    def put(self, user_data, user_id):
        user = UserModel.query.get(user_id)

        if user:    
            user.user_name = user_data["username"]
            user.password = user_data["password"]
            user.email = user_data["email"]
        else:
            user = UserModel(user_id= user_id, **user_data)
        db.session.add(user)
        db.session.commit()

        return user