import datetime
import os
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
from playhouse.db_url import connect

# DATABASE = SqliteDatabase('parkingAPP.db')
DATABASE = PostgresqlDatabase('parkingapp1')
# DATABASE = connect(os.environ.get('DATABASE_URL'))


class User(UserMixin, Model):
    username = CharField(max_length=100,unique=True)
    email = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)
    fullname = CharField(max_length=50)
    phoneNumber = CharField(max_length=100)
    address = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now())
    is_host = BooleanField(default=False)
    profileImgUrl = CharField(max_length=255, null=True, default= 'default.png')
    carPic = CharField(max_length=255, null=True, default='defcar.png')
    
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
        
    @classmethod
    def create_user(cls, username, email, password, fullname, phoneNumber, address, profileImgUrl='default.png', carPic='defcar.png', is_host=False):
        try:
            cls.create(
                username = username,
                email = email,
                password = generate_password_hash(password),
                fullname = fullname,
                phoneNumber = phoneNumber,
                address = address,
                is_host = is_host,
                profileImgUrl = profileImgUrl,
                carPic = carPic
            )
        except IntegrityError:
            raise ValueError("User already exists")

    def get_reservations(self):
        return Reservation.select().where(Reservation.user == self)

    def get_my_parkings(self):
        return Parking.select().where(Parking.user == self)

    def get_my_reviews(self):
        return Review.select().where(Review.user == self)


class Parking(Model):
    user = ForeignKeyField(
        model=User,
        backref='parking'
    )
    price = CharField()
    description = CharField()
    location = CharField()
    parkingPic = CharField(null=True, default='Logo.png')

    class Meta:
        database = DATABASE
        order_by = ('-user',)

    @classmethod
    def create_parking(cls, user, price, description, location, parkingPic='Logo.png'):
        try:
            cls.create(
                user = user,
                price = price,
                description = description,
                location = location,
                parkingPic = parkingPic
            )
        except IntegrityError:
            raise ValueError("Parking space already exist error")

    @classmethod
    def delete_parking(cls, parking_id):
        parking = Parking.get(Parking.id == parking_id)
        try:
            parking.delete()
        except IntegrityError:
            raise ValueError("No parking space exist")
        return 


class Reservation(Model):
    parking = ForeignKeyField(
        model = Parking,
        backref='reservations'
    )
    user = ForeignKeyField(
        model=User,
        backref='reservations'
    )
    resDate = CharField(unique=True, null=True)

    class Meta:
        database = DATABASE
        order_by = ('-parking',)

    @classmethod
    def create_res(cls, user, parking, resDate):
        try:
            cls.create(
                user = user,
                parking = parking,
                resDate = resDate
            )
        except IntegrityError:
            raise ValueError("Reservation already exist error")

    # @classmethod
    # def delete_res

class Review(Model):
    parking = ForeignKeyField(
        model = Parking,
        backref = 'reviews'
    )
    user = ForeignKeyField(
        model=User,
        backref='reviews'
    )
    review_date = DateField(default=datetime.datetime.now())
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-review_date',)

    @classmethod
    def create_review(cls, parking,user, content):
        try:
            cls.create(
                parking = parking,
                user = user,
                content = content
            )
        except IntegrityError:
            raise ValueError("Review error")

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Parking, Reservation, Review], safe=True)
    DATABASE.close()