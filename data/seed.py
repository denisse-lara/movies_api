import csv
import random
import sys
sys.path.insert(1, '../technical_challenge')

from faker import Faker
from werkzeug.security import generate_password_hash

from api.model.movie import Movie
from app import create_app, db
from api.model.user_profile import UserProfile

app = create_app()
fake = Faker()


def like_movie(users_arr, movies_arr):
    for user in users_arr:
        movie = random.choice(movies_arr)
        if not user.liked_movies.count(movie):
            # print(f"{user.username} liking movie {movie.title}")
            user.liked_movies.append(movie)


print("Seeding database")
with app.app_context():
    print("Dropping tables...")
    db.drop_all()
    print("Creating tables...")
    db.create_all()

    print("\nSaving admin user username='admin' password='admin'")
    # create admin
    admin = UserProfile(
        username="admin",
        password="admin",
        name="Admin",
        admin=True,
    )
    db.session.add(admin)
    db.session.commit()

    password = generate_password_hash("12345")
    admin = False
    print("Saving 100 new users, all with password=12345")
    banned = True
    for _ in range(100):
        name = fake.name()
        # prevent duplicate name from faker
        while UserProfile.query.filter_by(name=name).first():
            name = fake.name()
        username = "_".join(name.lower().split())

        new_user = UserProfile(
            username=username,
            password=password,
            name=name,
            admin=False,
            banned=banned,
        )
        db.session.add(new_user)
        if _ == 50:
            banned = False
    db.session.commit()

    with open("data/movies.tsv") as movies_file:
        movies_reader = csv.DictReader(movies_file, ["title", "release_year"])
        movies_reader = [
            movie for movie in movies_reader if movie["release_year"] != "\\N"
        ][1:]

        print("\nSaving all movies")
        print("This will take a while...")
        for movie in movies_reader:
            try:
                new_movie = Movie(
                    title=movie["title"], release_year=int(movie["release_year"]),
                    poster_img_url=""
                )
                db.session.add(new_movie)
            except ValueError:
                print(f'Skipping movie {movie["title"]} without release_year {movie["release_year"]}')
        db.session.commit()

    users = UserProfile.query.filter(UserProfile.username != "admin").all()
    movies = Movie.query.all()

    print("\nMaking users like movies")
    for _ in range(20):
        like_movie(users, movies)
    db.session.commit()

print("\nAdmin user credentials:")
print("username='admin' password='admin'")
print("Seeded database.")
