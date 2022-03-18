# Movies API

This project implements a movie api where users can register to like and unlike movies. It provides an administration route where admin users can add, modify and delete movies.

## API Documentation
Postman: https://documenter.getpostman.com/view/19926071/UVsMtQcP

## Setup

Start by creating a virtual environment:

```
virtualenv venv
source venv/bin/activate
```

Then install all the dependencies:

```
pip install -r local.txt
```

Then, make an .env file, add these variables, and change them to match your environment:

```
APP_SETTINGS=config.DevelopmentConfig
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your_seed

DATABASE_NAME=movieslikeddev
DB_USER=your_postgres_db_user
DB_HOST=your_postgres_db_host
DB_PORT=your_postgres_db_port
DB_PASSWORD=postgres
SQLALCHEMY_DATABASE_URI=postgresql:///movieslikeddev
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

Now, create and seed the database running the following commands:

```
python data/setup_db.py
python data/seed_db.py
```

You are ready to go. Run the app with:

```
python app.py
```