import datetime
import os
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('parkingAPP.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=20)
    fullname = CharField(max_length=50)
    phoneNumber = CharField(max_length=10)
    address = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now())
    is_host = BooleanField(default=False)
    profileImgUrl = CharField()
    carPic = CharField()
    
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
        
    @classmethod
    def create_user(cls, username, email, password, fullname, phoneNumber, address, profileImgUrl, carPic, host=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                fullname = fullname,
                phoneNumber = phoneNumber,
                address = address,
                is_host=host,
                profileImgUrl=profileImgUrl,
                carPic = carPic
            )
        except IntegrityError:
            raise ValueError("User already exists")

    # def get_parking(self):
    #     return Parking.select().where(Parking.user == self)

class Parking(Model):
    user = ForeignKeyField(
        model=User,
        backref='parking'
    )
    price = CharField()
    description = CharField()
    location = CharField()
    parkingPic = CharField()

    class Meta:
        database = DATABASE
        order_by = ('-user',)

    @classmethod
    def create_parking(cls, user, price, description, location, parkingPic):
        try:
            cls.create(
                user = user,
                price = price,
                description = description,
                location = location,
                parkingPic = parkingPic
            )
        except IntegrityError:
            raise ValueError("Parking space already error")

    @classmethod
    def delete_parking(cls, parking_id):
        parking = Parking.get(Parking.id == parking_id)
        try:
            parking.delete()
        except IntegrityError:
            raise ValueError("No parking space exist")
        return 

    @classmethod
    def get_reservations(self):
        return Reservation.select().where(Reservation.parking == self)

class Reservation(Model):
    parking = ForeignKeyField(
        model = Parking,
        backref='reservations'
    )
    resDate = DateField,
    duartion = CharField

    class Meta:
        database = DATABASE
        order_by = ('-parking',)

    # @classmethod
    # def create_res

    # @classmethod
    # def delete_res

class Review(Model):
    reservation = ForeignKeyField(
        model = Reservation,
        backref = 'reviews'
    )
    user = ForeignKeyField(
        model=User,
        backref='reviews'
    )
    review_date = DateField()
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-review_date',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Parking, Reservation, Review], safe=True)
    DATABASE.close()       