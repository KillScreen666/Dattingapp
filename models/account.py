from db import db

class AccountModel(db.Model):
    __tablename__ = "accounts"

    account_id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean(), nullable=False)

    users = db.relationship("UserModel", back_populates="account", lazy="dynamic", cascade="all, delete")