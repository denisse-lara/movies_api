from app import db


class JWTWhitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    token = db.Column(db.String(100), nullable=False, unique=True)

    def __str__(self):
        return f"user: '{self.user_id}'\ttoken: {self.token}"
