from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required

# db config
from db import db
from models import RoleModel, UserModel
from schemas import RoleSchema, RoleAndUserSchema

blp = Blueprint("Roles", "roles", description="Operations on roles")


@blp.route("/role")
class RoleList(MethodView):
    @blp.response(200, RoleSchema(many=True))
    @jwt_required()
    def get(self):
        return RoleModel.query.all()

    @blp.arguments(RoleSchema)
    @blp.response(201, RoleSchema)
    def post(self,role_data): 
        role = RoleModel(**role_data)

        try:
            db.session.add(role)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A role with that name already exists.",
            )    
        except SQLAlchemyError:
            abort(500, message="An error has occurred while creating the role.")

        return role    


@blp.route("/role/<int:role_id>")
class Role(MethodView):
    @blp.response(200, RoleSchema)
    @jwt_required()
    def get(self, role_id):
        role = RoleModel.query.get_or_404(role_id)
        return role


@blp.route("/user/<int:user_id>/role/<int:role_id>")
class LinkRolesToUser(MethodView):
    @blp.response(201, RoleSchema)
    @jwt_required(fresh=True)
    def post(self, user_id, role_id):
        user = UserModel.query.get_or_404(user_id)
        role = RoleModel.query.get_or_404(role_id)

        user.roles.append(role)

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the role.")

        return role

    @blp.response(200, RoleAndUserSchema)
    @jwt_required(fresh=True)
    def delete(self, user_id, role_id):
        user = UserModel.query.get_or_404(user_id)
        role = RoleModel.query.get_or_404(role_id)

        user.roles.remove(role)

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the role.")

        return {"message": "User removed from role", "user": user, "role": role}


@blp.route("/role/<int:role_id>")
class Role(MethodView):
    @blp.response(200, RoleSchema)
    @jwt_required(fresh=True)
    def get(self, role_id):
        role = RoleModel.query.get_or_404(role_id)
        return role

    @blp.response(
        202,
        description="Deletes a role if no user is roleged with it.",
        example={"message": "Role deleted."},
    )
    @blp.alt_response(404, description="Role not found.")
    @blp.alt_response(
        400,
        description="Returned if the role is assigned to one or more users. In this case, the role is not deleted.",
    )
    @jwt_required()
    def delete(self, role_id):
        role = RoleModel.query.get_or_404(role_id)

        if not role.users:
            db.session.delete(role)
            db.session.commit()
            return {"message": "Role deleted."}
        abort(
            400,
            message="Could not delete role. Make sure role is not associated with any users, then try again.",
        )