from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
import requests
from my_secrets import MOVIE_API
## This uses an API key from themoviedb.org.

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
    title = db.Column(db.String(80))
    year = db.Column(db.Integer)
    description = db.Column(db.String(200))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(200))
    img_url = db.Column(db.String(200))
# db.create_all()
#


# ## Add the first movie to the new db. After creation, it can be deleted, but it is kept here for review purposes.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# #
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
    all_movies = db.session.query(Movie).order_by(Movie.rating)
    ## List movies from top to bottom, with highest score as #1 at bottom.
    for rank in range(Movie.query.count()):
        all_movies[rank].ranking = (Movie.query.count()) - rank
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/delete/<int:num>", methods=['POST', 'GET'])
def delete(num):
    ## Delete function by click delete button under movie.
    film = Movie.query.filter_by(id=num).first()
    db.session.delete(film)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit/<int:num>", methods=['POST', 'GET'])
def edit(num):
    ## Edit movie rating and review by clicking button and filling out form.
    form = RateMovieForm()
    film = Movie.query.filter_by(id=num).first()
    movie_title = film.title
    if form.validate_on_submit():
        film.rating = form.user_rating.data
        film.review = form.user_review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie_title=movie_title)



@app.route("/add", methods=['POST', 'GET'])
def add():
    ## Search for new movie to add using TMDB API.
    ## The results are shown on the 'select' page to then be selected by the user.
    form = AddMovie()
    if form.validate_on_submit():
        request = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={MOVIE_API}&query={form.movie_title.data}').json()
        results = request["results"]
        return render_template("select.html", results=results)
    return render_template("add.html", form=form)

@app.route("/new/<int:movie_id>", methods=['POST', 'GET'])
def new(movie_id):
    ## Create a new movie entry in the database, when selected by user on the 'select' page.
    movie = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={MOVIE_API}").json()
    new_movie = Movie(
        title=movie["title"],
        year=movie["release_date"][0:4],
        description=movie["overview"],
        img_url=f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)