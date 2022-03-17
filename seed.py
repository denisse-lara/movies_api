import csv
import random
import sys

from faker import Faker
from werkzeug.security import generate_password_hash

from api.model.movie import Movie
from app import create_app, db
from api.model.user_profile import UserProfile

sys.path.append("../technical_challenge")

app = create_app()
fake = Faker()


def like_movie(users_arr, movies_arr):
    for user in users_arr:
        movie = random.choice(movies_arr)
        if not user.liked_movies.count(movie):
            print(f"{user.username} liking movie {movie.title}")
            user.liked_movies.append(movie)


print("Seeding database")
with app.app_context():
    print("Dropping")
    db.drop_all()
    print("Creating")
    db.create_all()

    print("\nSaving admin user")
    # create admin
    admin = UserProfile(
        username="admin",
        password="admin",
        display_name="Admin",
        admin=True,
    )
    db.session.add(admin)
    db.session.commit()

    password = generate_password_hash("password")
    admin = False
    print("\nSaving 100 new users")
    banned = True
    for _ in range(100):
        name = fake.name()
        username = "_".join(name.lower().split())

        new_user = UserProfile(
            username=username,
            password=password,
            display_name=name,
            admin=False,
            banned=banned,
        )
        print(repr(new_user))
        db.session.add(new_user)
        if _ == 50:
            banned = False
    db.session.commit()

    with open("data/movies.tsv") as movies_file:
        movies_reader = csv.DictReader(movies_file, ["title", "release_year"])
        print("\nChoosing 500 movies")
        movies_reader = random.choices(list(movies_reader), k=500)
        movies_reader = [
            movie for movie in movies_reader if movie["release_year"] != "\\N"
        ]

        print("Saving 500 movies")
        for movie in movies_reader:
            new_movie = Movie(
                title=movie["title"], release_year=int(movie["release_year"])
            )
            print(repr(new_movie))
            db.session.add(new_movie)
        db.session.commit()

    users = UserProfile.query.filter(UserProfile.username != "admin").all()
    movies = Movie.query.all()

    # make users like around 10 movies
    for _ in range(10):
        like_movie(users, movies)
    db.session.commit()

print("\nAdmin user credentials:")
print("username='admin' password='admin'")
print("Seeded database.")
