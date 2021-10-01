from pprint import pprint
from opencage.geocoder import OpenCageGeocode
from amadeus import Client, ResponseError, Location
from flask import Flask, render_template, request, jsonify, flash, session, g
from werkzeug.utils import redirect
from models import db, connect_db, User, Country, Unesco, Destination, VisitedCountry
from forms import EditUserForm, SignUpForm, LoginForm
import json

import os
import psycopg2

from sqlalchemy.exc import IntegrityError

from restcountries import RestCountryApiV2 as rapi
rapi.BASE_URI = "https://restcountries.com/v2"

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'MissMillieIsGood')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URI', 'postgresql:///travel-app')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

amadeus = Client(
    client_id=os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SECRET'),
    hostname=os.environ.get('HOSTNAME')
)

# amadeus = Client(
#     client_id=config.client_id,
#     client_secret=config.client_secret,
#     hostname=config.hostname
# )

geocode_key = os.environ.get('GEOCODE_KEY')
geocoder = OpenCageGeocode(geocode_key)

# geocode_key = config.geocode
# geocoder = OpenCageGeocode(geocode_key)

CURR_USER_KEY = "curr_user"

connect_db(app)

# LOGGING IN AND OUT


@app.before_request
def add_global_user():
    '''If you are logged in, you will be added as the Global User'''

    g.user = None

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])


def do_login(user):
    '''Log In A User'''

    session[CURR_USER_KEY] = user.username


def do_logout():
    '''Log Out A User'''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# HOME ROUTE


@app.route('/')
def home_page():
    '''Home page for the app'''

    countries = Country.query.order_by(Country.nicename.asc()).all()

    return render_template('home.html', countries=countries)

# COUNTRIES ROUTES


@app.route('/countries')
def show_countries():

    countries = Country.query.order_by(Country.nicename.asc()).all()

    return render_template('countries.html', countries=countries)


@app.route('/countries/<nicename>')
def show_country(nicename):
    country = Country.query.get(nicename)

    # due to a change in the rest countries API, we no longer need the filters
    country_search = rapi.get_countries_by_name(nicename)
    cap_country = (f'{country_search[0].capital}, {country_search[0].name}')
    coords = geocoder.geocode(cap_country)

    if country.lat == "None" or country.lng == "None":
        country.lat = coords[0]['geometry']['lat']
        country.lng = coords[0]['geometry']['lng']
        db.session.commit()

    if country.safety_rating == "None":
        country.safety_rating = json.dumps(amadeus.safety.safety_rated_locations.get(latitude=country.lat,
                                                                                     longitude=country.lng).data)
    if country.pois == "None":
        country.pois = json.dumps(amadeus.reference_data.locations.points_of_interest.get(latitude=country.lat,
                                                                                          longitude=country.lng).data)
    if country.tours == "None":
        country.tours = json.dumps(amadeus.shopping.activities.get(latitude=country.lat,
                                                                   longitude=country.lng).data)

    db.session.commit()

    return render_template('country.html', country=country_search[0],
                           safety_ratings=json.loads(country.safety_rating),
                           pois=json.loads(country.pois), tours=json.loads(country.tours))


@app.route('/unesco-sites')
def unesco_sites():
    return "these incredible sights are often rife with cultural/historical significance, or are natural wonders"

# LOGIN AND SIGNUP ROUTES


@app.route('/signup', methods=["GET", "POST"])
def sign_up():
    '''Handles user signup'''
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                img_url=form.img_url.data or User.img_url.default.arg,
                bio=form.bio.data
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash("username is taken", "danger")
            return render_template('signup.html', form=form)

        do_login(user)
        flash(f"Thank you for signing up, {user.username}!", "success")

        return redirect('/')

    return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():

    form = LoginForm()

    if form.validate_on_submit:
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}", "success")
            return redirect('/')
        else:
            flash("Username or Password Not Correct")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop(CURR_USER_KEY)
    flash("You have logged out.", "success")
    return redirect('/')

# USER PAGE


@app.route('/users/<username>')
def user_page(username):
    user = User.query.get_or_404(username)
    destinations = Destination.query.all()
    visited_countries = VisitedCountry.query.all()
    return render_template('user.html', user=user,
                           destinations=destinations,
                           visited_countries=visited_countries)


@app.route('/users/<username>/edit-profile', methods=["GET", "POST"])
def edit_profile(username):
    '''Update the current user's profile'''
    user = User.query.get_or_404(username)

    form = EditUserForm()

    if g.user == user:

        if form.validate_on_submit():
            user.bio = form.bio.data
            user.img_url = form.img_url.data or User.img_url.default.arg
            db.session.commit()
            flash("Your profile has been updated!", "success")
            return redirect(f'/users/{g.user.username}')

        return render_template('edituser.html', user=user, form=form)

    else:
        flash("You cannot edit another user's profile.", "danger")
        return redirect(f'/users/{g.user.username}')


@app.route('/users/<username>/delete-profile', methods=["GET", "POST"])
def delete_profile(username):
    '''Delete a user's Dream Destinations account'''

    user = User.query.get_or_404(username)

    if g.user == user:
        do_logout()
        db.session.delete(g.user)
        db.session.commit()
        flash("Sorry to see you go! Your account has been deleted", "success")
        return redirect('/')

    else:
        flash("You cannot delete another user's profile!", "danger")
        return redirect(f'/users/{g.user.username}')

# ADDING DESTINATIONS


@app.route('/countries/<nicename>/add-dream-dest', methods=["POST"])
def add_dreamdest(nicename):
    '''Adding a country to a user's dream destinations list'''

    country = Country.query.get_or_404(nicename)
    user = User.query.get_or_404(g.user.username)

    for destination in user.destinations:
        if destination.country_name == country.nicename:
            flash(f"{nicename} is already in your Dream Destinations list!", "danger")
            return redirect(f'/countries/{nicename}')

    new_dest = Destination(
        user=g.user.username,
        country_name=country.nicename
    )

    db.session.add(new_dest)
    db.session.commit()
    flash(f"Added {nicename} to your dream destinations list!", "success")
    return redirect(f'/countries/{nicename}')


@app.route('/destinations/<id>/remove')
def remove_desination(id):
    '''Remove a destination from your Dream Destination List'''

    dream_destination = Destination.query.get_or_404(id)

    if not g.user:
        flash('You cannot edit this list.', 'danger')
        return redirect('/')

    if g.user.username != dream_destination.user:
        flash('You cannot edit this list.', 'danger')
        return redirect('/')

    g.user.destinations.remove(dream_destination)
    db.session.commit()
    flash(f'{dream_destination.country_name} has been removed from your list', 'success')

    return redirect(f'/users/{g.user.username}')


@app.route('/countries/<nicename>/add-been-there', methods=["POST"])
def add_done(nicename):
    country = Country.query.get_or_404(nicename)
    visited_dest = VisitedCountry(
        user=g.user.username,
        country_name=country.nicename
    )
    db.session.add(visited_dest)
    db.session.commit()
    flash(f"Added {nicename} to your been there list!", "success")
    return redirect(f'/countries/{nicename}')

# Error Handlers


@app.errorhandler(404)
def page_not_found(e):
    '''For errors'''

    return render_template('404.html')


@app.errorhandler(500)
def other_error(e):
    '''For errors'''

    return render_template('404.html')

### TEST ROUTES ###


@app.route('/test')
def test_app():
    location = request.args["location"]
    result = amadeus.shopping.flight_destinations.get(origin=location)
    return result


@app.route('/test2')
def test_2():
    # res = amadeus.shopping.activities.get(latitude=40.0, longitude=3.7)
    res = amadeus.reference_data.locations.point_of_interest(
        '9CB40CB5D0').get()
    return jsonify(res.data)


@app.route('/test-likes')
def test_3(curr_user):
    curr_user = User.query.get(session[CURR_USER_KEY])
    return curr_user.destinations
