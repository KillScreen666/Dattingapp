from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required


# db config
from db import db
from models import AccountModel
from schemas import AccountSchema


blp = Blueprint("Account", "account", description="Operations on accounts")

@blp.route("/hello")
def hello():
    return "hello world"

@blp.route("/account")
class AccountList(MethodView):
    @blp.response(200, AccountSchema(many=True))
    @jwt_required()
    def get(self):
        return AccountModel.query.all()

    @blp.arguments(AccountSchema)
    @blp.response(201, AccountSchema)
    @jwt_required()
    def post(self, account_data): 
        account = AccountModel(**account_data)

        try:
            db.session.add(account)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error has occurred while creating the account.")

        return account    


@blp.route("/account/<string:account_id>")
class Account(MethodView):
    @blp.response(200, AccountSchema)
    @jwt_required()
    def get(self, account_id):
        account = AccountModel.query.get_or_404(account_id)
        return account

    @jwt_required(fresh=True)
    def delete(cls, account_id):
        account = AccountModel.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()
        return {"message": "Account has been deleted."}


