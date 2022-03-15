import sys
sys.path.append('../technical_challenge')

from app import create_app, db
from api.model.user_profile import UserProfile

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()


def add_admin_user():
    with app.app_context():
        # create admin user
        admin = UserProfile.query.filter_by(username="admin").first()
        if not admin:
            admin = UserProfile(
                username="admin",
                password="admin",
                display_name="Admin",
                admin=True,
            )
            db.session.add(admin)
            db.session.commit()


add_admin_user()
