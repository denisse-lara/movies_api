from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from api.model.user_profile import UserProfile


class UserProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserProfile
        load_instance = True

    public_id = auto_field()
    username = auto_field()
    password = auto_field()
    display_name = auto_field()
    admin = auto_field()
    banned = auto_field()
