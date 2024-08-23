import os
import secrets

from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask import Flask, jsonify
from blocklist import BLOCKLIST

from db import db

import models

from resources.user import blp as UserBlueprint
from resources.account import blp as AccountBlueprint
from resources.role import blp as RoleBlueprint
# from resources.user_roles import blp as UserRolesBlueprint

def create_app(db_url=None):
    app = Flask(__name__)

    app.config["API_TITLE"] = "Datting App REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    # to generate a key (just once and not everytime the app runs) we need to open the python enviroment.
    # in terminal, type "python", "import secrets", "secrets.SystemRandom().getrandbits(128)"
    # grab that value and paste it below.
    # app.config["JWT_SECRET_KEY"] = secrets.SystemRandom().getrandbits(128)
    # teste
    app.config["JWT_SECRET_KEY"] = '299987847446707773371706040142321288768'
    jwt = JWTManager(app)

    # Token handling
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )
    
    # token blocklist
    # TODO: usar o Flask-Redis para fazer o token blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST


    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )
    
    # token refresh handler
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )



    api.register_blueprint(AccountBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(RoleBlueprint)

    return app