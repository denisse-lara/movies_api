from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.model.user_profile import UserProfile


class UserProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserProfile
        load_instance = True
        exclude = ("id", "password")
