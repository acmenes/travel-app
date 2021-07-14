'''For user and destinations models'''

from sqlalchemy.sql.schema import ForeignKey
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    '''App User'''

    __tablename__ = "users"

    username = db.Column(db.String(20), nullable=False, unique=True, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String)
    bio = db.Column(db.String(150))

    destinations = db.relationship('Destination')
    visited_countries = db.relationship('VisitedCountry')
    
    @classmethod
    def signup(cls, username, password, img_url, bio):
        hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, password=hashed_password, img_url=img_url, bio=bio)

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

        if user:
            authenticated = bcrypt.check_password_hash(user.password, password)
            if authenticated:
                return user

        return False

## create classes for dream destinations and been there done thats

# I want this Country model to reflect the countries CSV I downloaded

class Country(db.Model):
    '''Every country in the world'''

    __tablename__ = 'countries'

    id = db.Column(db.Integer)
    iso = db.Column(db.String)
    name = db.Column(db.String)
    nicename = db.Column(db.String, primary_key=True)
    iso3 = db.Column(db.String)

class Unesco(db.Model):
    '''Using this list, share a list of UNESCO sites in each country'''

    __tablename__ = 'usites'

    category = db.Column(db.String)
    country_en = db.Column(db.String, primary_key=True)
    region_en = db.Column(db.String)
    unique_number = db.Column(db.String)
    id_no = db.Column(db.String)
    rev_bis = db.Column(db.String)
    name = db.Column(db.String)
    short_description = db.Column(db.String)
    justification_en = db.Column(db.String)
    date_inscribed = db.Column(db.String)
    secondary_dates = db.Column(db.String)
    danger = db.Column(db.String, nullable=True)
    date_end = db.Column(db.String, nullable=True)
    danger_list = db.Column(db.String)
    longitude = db.Column(db.String)
    latitude = db.Column(db.String)
    hectares = db.Column(db.String)
    criteria_txt = db.Column(db.String)
    category_short = db.Column(db.String)
    iso_code = db.Column(db.String)
    udnp_code = db.Column(db.String)
    transboundary = db.Column(db.String)

class Destination(db.Model):

    __tablename__ = "destinations"

    user = db.Column(db.String, db.ForeignKey('users.username'))
    country_name = db.Column(db.String, db.ForeignKey('countries.nicename'), primary_key=True)

class VisitedCountry(db.Model):

    __tablename__ = "visited_countries"

    user = db.Column(db.String, db.ForeignKey('users.username'))
    country_name = db.Column(db.String, db.ForeignKey('countries.nicename'), primary_key=True)

def connect_db(app):
    '''Connect to the app'''

    db.app = app
    db.init_app(app)