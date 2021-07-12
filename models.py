'''For user and destinations models'''

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

class Country(db.Model):
    '''Every country in the world'''

    __tablename__ = 'countries'

    code = db.Column(db.String)
    country_name = db.Column(db.String, primary_key=True)

def connect_db(app):
    '''Connect to the app'''

    db.app = app
    db.init_app(app)