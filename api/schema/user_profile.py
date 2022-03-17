from api.model.user_profile import UserProfile
from api.schema.movie import MovieSchema
from app import ma


class UserProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserProfile
        load_instance = True
        exclude = ("id", "password")

    liked_movies = ma.Nested(MovieSchema, many=True)
