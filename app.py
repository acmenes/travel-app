from flask import Flask, render_template, request, jsonify, flash, session, g
from werkzeug.utils import redirect
from models import db, connect_db, User, Country, Unesco, Destination, VisitedCountry
from forms import SignUpForm, LoginForm

from sqlalchemy.exc import IntegrityError

from restcountries import RestCountryApiV2 as rapi
from amadeus import Client, ResponseError, Location
from opencage.geocoder import OpenCageGeocode
from pprint import pprint

app = Flask(__name__)

app.config['SECRET_KEY'] = "MissMillieIsGood"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///travel-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

### test key
# amadeus = Client(
#     client_id='GG2OA3MfjLRuOGzGavkdcHcWGCMKHws7',
#     client_secret='qB6Ix6NuAsBwx0m8'
# )

### prod key

amadeus = Client(
    client_id='xASzeerH5RXb2vb0ZJKdTCngmK6mI0Ur',
    client_secret='zAfkOnTUieumHNmo',
    hostname='production'
)

geocode_key = '31bce992a33045daadc50ea7e0902774'
geocoder = OpenCageGeocode(geocode_key)

CURR_USER_KEY = "curr_user"

connect_db(app)

### LOGGING IN AND OUT

@app.before_request
def add_global_user():
    '''If you are logged in, you will be added as the Global User'''

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    '''Log In A User'''

    session[CURR_USER_KEY] = user.username

def do_logout():
    '''Log Out A User'''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

### HOME ROUTE

@app.route('/')
def home_page():
    return render_template('home.html')

# use the geocode to connect to amadeus 

### CONUTRIES ROUTES

@app.route('/countries')
def show_countries():

    countries = Country.query.all()

    return render_template('countries.html', countries=countries)

@app.route('/countries/<nicename>')
def show_country(nicename):
    country = Country.query.get(nicename)
    country_search = rapi.get_countries_by_name(nicename, 
                                        filters=["name", 
                                        "capital", 
                                        "flag", 
                                        "currencies",
                                        "languages"])
    cap_country = (f'{country_search[0].capital}, {country_search[0].name}')
    coords = geocoder.geocode(cap_country)
    safety_rating = amadeus.safety.safety_rated_locations.get(latitude=coords[0]['geometry']['lat'],
                                                              longitude=coords[0]['geometry']['lng'])
    pois = amadeus.reference_data.locations.points_of_interest.get(latitude=coords[0]['geometry']['lat'],
                                                              longitude=coords[0]['geometry']['lng'])
    tours = amadeus.shopping.activities.get(latitude=coords[0]['geometry']['lat'],
                                            longitude=coords[0]['geometry']['lng'])
    return render_template('country.html', country=country_search[0], 
                                        safety_ratings=safety_rating.data,
                                        pois=pois.data, tours=tours.data)

@app.route('/country')
def country_page():
    # country_from_db = Country.query.get_or_404(country)
    country_search = request.args["country-search"]
    country = rapi.get_countries_by_name(country_search, 
                                        filters=["name", 
                                        "capital", 
                                        "flag", 
                                        "currencies",
                                        "languages"])
    return redirect(f'/countries/{country_search}')

@app.route('/unesco-sites')
def unesco_sites():
    return "these incredible sights are often rife with cultural/historical significance, or are natural wonders"

### LOGIN AND SIGNUP ROUTES

@app.route('/signup', methods=["GET", "POST"])
def sign_up():
    '''Handles user signup'''
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username = form.username.data,
                password = form.password.data,
                img_url = form.img_url.data,
                bio = form.bio.data
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash("username is taken", "danger")
            return render_template('signup.html', form=form)
        
        do_login(user)
        flash("Thank you for signing up!", "success")
    
        return redirect('/')

    else:
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
    flash("You have logged out.")
    return redirect('/')

## USER PAGE

@app.route('/users/<username>')
def user_page(username):
    user = User.query.get_or_404(username)
    destinations = Destination.query.all()
    visited_countries = VisitedCountry.query.all()
    return render_template('user.html', user=user, 
                                        destinations=destinations, 
                                        visited_countries=visited_countries)

### ADDING DESTINATIONS

@app.route('/countries/<nicename>/add-dream-dest', methods=["POST"])
def add_dreamdest(nicename):
    '''Adding a country to a user's dream destinations list'''

    country = Country.query.get_or_404(nicename)

    new_dest = Destination(
        user = g.user.username,
        country_name = country.nicename
    )
    ## this doesn't seem to work
    # if new_dest in g.user.destinations:
    #     flash("This country is already on your Dream Destinations List!", "danger")
    #     return redirect(f'/countries/{nicename}')
  
    db.session.add(new_dest)
    db.session.commit()
    flash("Added to dream destinations!", "success")
    return redirect(f'/countries/{nicename}')

@app.route('/countries/<nicename>/remove-dream-dest', methods=["POST"])
def remove_dreamdest(nicename):
    '''Removing a destination from your list'''

    dream_destination = Destination.query.get_or_404(nicename)
    g.user.destinations.remove(dream_destination)
    db.session.commit()
    flash("This destination has been removed from your list", "danger")

    return redirect(f'/countries/{nicename}')


@app.route('/countries/<nicename>/add-been-there', methods=["POST"])
def add_done(nicename):
    country = Country.query.get_or_404(nicename)
    visited_dest = VisitedCountry(
        user = g.user.username,
        country_name = country.nicename
    )
    db.session.add(visited_dest)
    db.session.commit()
    flash("Added to your been there list!", "sucess")
    return redirect(f'/countries/{nicename}')

### Error Handlers

@app.errorhandler(404)
def page_not_found(e):
    '''For errors'''

    return redirect('404.html'), 404

### TEST ROUTES ###

@app.route('/test')
def test_app():
    location = request.args["location"]
    result = amadeus.shopping.flight_destinations.get(origin=location)
    return result

@app.route('/test2')
def test_2():
    # res = amadeus.shopping.activities.get(latitude=40.0, longitude=3.7)
    res = amadeus.reference_data.locations.point_of_interest('9CB40CB5D0').get()
    return jsonify(res.data)

@app.route('/test-likes')
def test_3(curr_user):
    curr_user = User.query.get(session[CURR_USER_KEY])
    return curr_user.destinations