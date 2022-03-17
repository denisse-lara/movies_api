import uuid

from sqlalchemy import event

from app import db


class Movie(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer)
    poster_img_url = db.Column(db.String(255))

    def __str__(self):
        return f"'title: {self.title}' id: {self.id}"

    def __repr__(self):
        return (
            f"Movie(title='{self.title}', release_year={self.release_year}, "
            f"poster_img_url='{self.poster_img_url}')"
        )


@event.listens_for(Movie, "before_insert")
def hash_password(mapper, connection, target):
    target.public_id = str(uuid.uuid4())


movie_like = db.Table(
    "movie_like",
    db.Column("movie_id", db.Integer, db.ForeignKey("movie.id"), primary_key=True),
    db.Column(
        "user_id", db.Integer, db.ForeignKey("user_profile.id"), primary_key=True
    ),
)
