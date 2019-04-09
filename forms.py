from flask_wtf import FlaskForm as Form 
from models import User
from models import Parking
from models import Reservation
from wtforms import StringField, PasswordField, TextAreaField, TextField, SubmitField, IntegerField, BooleanField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email, Length, EqualTo)
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import DateField

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

class SignUpForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    fullname= StringField(
        'Full Name',
        validators=[
            DataRequired(),
            Length(min=2),
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )
    phoneNumber = StringField(
        'Phone Number',
        validators=[DataRequired()]
    )
    address = StringField(
        'Address',
        validators=[DataRequired()]
    )

class UpdateProfile(Form):
    username = StringField('Username')
    email = StringField('Email')
    fullname= StringField(
        'Full Name',
        validators=[
            DataRequired(),
            Length(min=2),
        ]
    )
    phoneNumber = StringField(
        'Phone Number',
        validators=[DataRequired()]
    )
    address = StringField(
        'Address',
        validators=[DataRequired()]
    )
    profileImgUrl = FileField("Update Profile Picture", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    carPic = FileField("Update Car Picture", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])


class SignInForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class HostForm(Form):
    is_host = BooleanField()

class ParkingForm(Form):
    price= TextField('Price')
    description = TextField('Description')
    location = TextField('Address')
    parkingPic = FileField("Update a picture of your driveway", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])

class ResForm(Form):
    resDate = TextField('Reservation Date')
    duration = TextField('Duration')
    
class ReviewForm(Form):
    content = TextField()
