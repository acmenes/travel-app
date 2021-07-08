'''For user and destinations models'''

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    '''App User'''

    __tablename__ = "users"

    username = db.Column(db.String(20), nullable=False, unique=True)
    bio = db.Column(db.String(150))
    password = db.Column(db.Text, nullable=False)
    # destinations = db.Relationship("Destination")

    @classmethod
    def signup(cls, username, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, password=password)

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