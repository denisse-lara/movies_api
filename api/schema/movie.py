from marshmallow import fields

from api.model.movie import Movie
from app import ma


class MovieSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Movie
        load_instance = True
        exclude = ("id",)

    likes = fields.Method("get_likes", deserialize="load_likes")

    def get_likes(self, obj):
        return len(obj.likes)

    def load_likes(self, value):
        return int(value)
