from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import requests
import secrets



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

## Setup new db info with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

## Create new DB.
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String(200), unique=True, nullable=False)
    rating = db.Column(db.Float, unique=True, nullable=False)
    ranking = db.Column(db.Integer, unique=True, nullable=False)
    review = db.Column(db.String(200), unique=True, nullable=False)
    img_url = db.Column(db.String(200), unique=True, nullable=False)
# db.create_all()

## Add the first movie to the new db.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()

## Add movie function with WTForms.
class AddMovie(FlaskForm):
    movie_title = StringField("Movie Title")
    submit = SubmitField("Add Movie")


## Rate/review movie functionality with WTForms.
class RateMovieForm(FlaskForm):
    user_rating = IntegerField("Your Rating")
    user_review = StringField("Your Review")
    submit = SubmitField("Submit")

@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)

@app.route("/delete/<int:num>", methods=['POST', 'GET'])
def delete(num):
    film = Movie.query.filter_by(id=num).first()
    db.session.delete(film)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit/<int:num>", methods=['POST', 'GET'])
def edit(num):
    form = RateMovieForm()
    film = Movie.query.filter_by(id=num).first()
    movie_title = film.title
    if form.validate_on_submit():
        film.rating = form.user_rating.data
        film.review = form.user_review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie_title=movie_title)



    return render_template("edit.html")


# @app.route("/add")
# def add():
#     return render_template("add.html")

if __name__ == '__main__':
    app.run(debug=True)
