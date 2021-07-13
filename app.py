from flask import Flask, render_template, request, jsonify, flash, session, g
from werkzeug.utils import redirect
from models import db, connect_db, User, Country, Unesco
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

amadeus = Client(
    client_id='GG2OA3MfjLRuOGzGavkdcHcWGCMKHws7',
    client_secret='qB6Ix6NuAsBwx0m8'
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

@app.route('/all-countries')
def show_countries():

    countries = Country.query.all()

    return render_template('countries.html', countries=countries)

@app.route('/country')
def country_page():
    country_search = request.args["country-search"]
    country = rapi.get_countries_by_name(country_search, 
                                        filters=["name", 
                                        "capital", 
                                        "flag", 
                                        "currencies",
                                        "languages"])
    return render_template('country.html', country=country[0])

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
            return redirect('/login')

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
    return render_template('user.html', user=user)

### ADDING DESTINATIONS

@app.route('/add-dream-dest')
def add_dreamdest():
    return "Added"

@app.route('/add-been-there')
def add_done():
    return "Added"

### TEST ROUTES ###

@app.route('/test')
def test_app():
    location = request.args["location"]
    result = amadeus.shopping.flight_destinations.get(origin=location)
    return result

@app.route('/test2')
def test_2():
    res = amadeus.shopping.activities.get(latitude=39.9042, longitude=116.4074)
    return jsonify(res.data)