from flask_wtf import FlaskForm as Form 
from models import User
from models import Parking
from models import Reservation
from wtforms import StringField, PasswordField, TextAreaField, TextField, SubmitField, IntegerField, DateField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email, Length, EqualTo)

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
    profileImgUrl = StringField("Profile Image")
    carPic = StringField(
        "Car Image",
        # validators=[DataRequired()]
    )

class SignInForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class ResForm(Form):
    date = DateField(
        'Reservation Date',
        validators=[DataRequired()]
    )
    duration = IntegerField(
        'Duration',
        validators=[DataRequired()]
    )
    submit = SubmitField('Create Reservation')

class Review(Form):
    reviewText = TextAreaField()
    submit = SubmitField('Create Review')