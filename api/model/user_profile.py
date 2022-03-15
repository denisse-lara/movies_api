import uuid

from werkzeug.security import generate_password_hash
from sqlalchemy import event

from app import db


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=True, default="")
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    display_name = db.Column(db.String(50))
    banned = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __str__(self):
        return f"'{self.username}'\tid: {self.id}\tadmin: {self.admin}"

    def __repr__(self):
        return (
            f"UserProfile(username='{self.username}', password='{self.password}',"
            f" display_name='{self.display_name}')"
        )


@event.listens_for(UserProfile, "before_insert")
def hash_password(mapper, connection, target):
    target.public_id = str(uuid.uuid4())
    target.password = generate_password_hash(password=target.password)
