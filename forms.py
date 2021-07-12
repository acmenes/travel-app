from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, InputRequired, Length


class SignUpForm(FlaskForm):
    '''Form for signing up for Dream Destinations'''

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    bio = TextAreaField('About You')
    img_url = StringField('Image URL')

class LoginForm(FlaskForm):
    '''Form for logging into your account'''

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
