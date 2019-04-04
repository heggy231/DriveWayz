from flask import Flask, g, session
from flask import render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import os
import models 
import forms 
import json


DEBUG = True
PORT = 8000

app = Flask(__name__)
app.secret_key = 'adkjfalj.adflja.dfnasdf.asd'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


def handle_signup(form):
    flash('Welcome new member!!!', 'success')
    user = models.User.create_user(
        username=form.username.data,
        email=form.email.data,
        password=form.password.data,
        fullname=form.fullname.data,
        phoneNumber=form.phoneNumber.data,
        address=form.address.data,
        profileImgUrl=form.profileImgUrl.data,
        carPic=form.carPic.data,
        )
    db.session.add(user)
    db.session.commit()
    session['email'] = user.email 

    return redirect(url_for('index'))

def handle_login(form):
    try:
        user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
        flash("your email or password doesn't match", "error")
    else:
        if check_password_hash(user.password, form.password.data):
            ## creates session
            login_user(user)
            flash('Hi! You have successfully Signed In!!!', 'success signin')
            return redirect(url_for('index'))
        else:
            flash("your email or password doesn't match", "error")

@app.route('/', methods=('GET', 'POST'))
def index():
    log_in_form = forms.SignInForm()
    sign_up_form = forms.SignUpForm()
    parkings = models.Parking.select()

    if sign_up_form.validate_on_submit():
        handle_signup(sign_up_form)

    elif log_in_form.validate_on_submit():
        handle_login(log_in_form)
        
    return render_template('auth.html', sign_up_form=sign_up_form, log_in_form=log_in_form, parkings=parkings)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for('index'))


# @app.route('/homepage', methods=['GET'])
# @login_required
# def homepage():
#     parkings = models.Parking.select()
    
#     return render_template('homepage.html', parkings=parkings )

@app.route('/parking/<parkingid>', methods=['GET','POST'])
def parking(parkingid):
    parking_model = models.Parking.get_by_id(int(parkingid))

    form = forms.ResForm()
    if form.validate_on_submit():
        models.Reservation.create(
            user=g.user._get_current_object(),
            resDate=form.resDate.data,
            duration=form.duration.data,
            carPic=form.carPic.data,
            parking=parking_model)

        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('parkingspace.html', parking=parking_model, form=form, reservation={'resDate':'','duration':''})

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profilepage(username):
    user = models.User.get(models.User.username == username)
    reservations = current_user.get_reservations()
    
    form = forms.HostForm()
    if form.validate_on_submit():
        user.is_host = form.is_host.data
        user.save()
        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('user.html', user=user,form=form, reservations=reservations) 


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username = 'Homer',
            email = 'homer@ga.com',
            fullname = 'Homer Simpson',
            password = '123',
            phoneNumber = '4151234567',
            address = '123 Fake St.',
            profileImgUrl = 'http://interactive.nydailynews.com/2016/05/simpsons-quiz/img/simp1.jpg',
            carPic = 'http://fcauthority.com/wp-content/uploads/2017/01/Homers-Car-700x340.jpg',
            is_host = False
            )
        models.User.create_user(
            username = 'Ned',
            email = 'ned@ga.com',
            fullname = 'Ned Flanders',
            password = '123',
            phoneNumber = '4151234567',
            address = 'Evergreen Terrace, Springfield',
            profileImgUrl = 'https://i.imgflip.com/acs9p.jpg',
            carPic = 'http://fcauthority.com/wp-content/uploads/2017/01/Homers-Car-700x340.jpg',
            is_host = False
            )
        models.Parking.create_parking(
            user = 1,
            price = '$25',
            description = 'OK parking space',
            location = 'Evergreen terrace, springfield',
            parkingPic = 'https://images.unsplash.com/14/unsplash_5243e9ef164a5_1.JPG?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
        )
        models.Parking.create_parking(
            user = 2,
            price = '$10',
            description = 'Friendly neighbors parking space',
            location = 'Evergreen terrace, springfield',
            parkingPic = 'https://images.unsplash.com/photo-1465301055284-72f355cfd745?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
        )
        models.Parking.create_parking(
            user = 2,
            price = '$15',
            description = 'Safe parking space',
            location = 'Sketchy St, springfield',
            parkingPic = 'https://images.unsplash.com/photo-1527377667-83c6c76f963f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
        )

        models.Reservation.create_res(
            user = 2,
            parking = 1,
            resDate = '5-5-19',
            duration = '1 day',
            carPic = 'http://fcauthority.com/wp-content/uploads/2017/01/Homers-Car-700x340.jpg'
        )

    except ValueError:
        pass


    app.run(debug=DEBUG, port=PORT)