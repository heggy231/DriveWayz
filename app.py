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
    # g.db.session.add(user)
    # g.db.session.commit()
    # session['email'] = user.email 

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


@app.route('/parking/<parkingid>', methods=['GET','POST'])
def parking(parkingid):
    parking_model = models.Parking.get_by_id(int(parkingid))
    reviews = models.Review.select().where(models.Review.parking_id==int(parkingid))
    review_form = forms.ReviewForm()

    form = forms.ResForm()
    if form.validate_on_submit():
        models.Reservation.create(
            user=g.user._get_current_object(),
            resDate=form.resDate.data,
            duration=form.duration.data,
            carPic=form.carPic.data,
            parking=parking_model)
        flash('The date you selected is already booked.')

        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('parkingspace.html', parking=parking_model, form=form, reviews = reviews, review_form=review_form, reservation={'resDate':'','duration':''})


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profilepage(username):
    user = models.User.get(models.User.username == username)
    parkings =  current_user.get_my_parkings()
    parking =  current_user.get_my_parkings()
    reservations = current_user.get_reservations()
    parking_form = forms.ParkingForm()
    reviews = current_user.get_my_reviews()
    profileImgUrl = url_for('static', filename='profile_pics/' + current_user.profileImgUrl)
    carPic = url_for('static', filename='profile_pics/' + current_user.carPic)

    form = forms.HostForm()
    if form.validate_on_submit():
        user.is_host = form.is_host.data
        user.save()

    return render_template('user.html', user=user,form=form, reservations=reservations, parking=parking,parkings=parkings, parking_form=parking_form, reviews=reviews, profileImgUrl=profileImgUrl, carPic=carPic) 

@app.route('/profile/<resid>/delete')
@login_required 
def delete_res(resid):
    reservation = models.Reservation.get(models.Reservation.id == resid)
    reservation.delete_instance()

    return redirect(url_for('profilepage', username=g.user._get_current_object().username))

@app.route('/reservation/<resid>/edit', methods=['GET','POST'])
def edit_res(resid):
    reservation = models.Reservation.get(models.Reservation.id == resid)
    
    form = forms.ResForm()
    if form.validate_on_submit():
        reservation.resDate = form.resDate.data
        reservation.duration = form.duration.data
        reservation.carPic = form.carPic.data
        reservation.save()
        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('reservation.html', form=form, reservation=reservation)

@app.route('/profile/<username>/createspace', methods=['POST'])
def createspace(username):
    form = forms.ParkingForm()
    if form.validate_on_submit():
        models.Parking.create_parking(
            user=g.user._get_current_object(),
            price = form.price.data,
            description = form.description.data,
            location =form.location.data,
            parkingPic = form.parkingPic.data
        )
    return redirect(url_for('profilepage', username=g.user._get_current_object().username))

@app.route('/profile/<parkingid>/managespace', methods=['GET','POST'])
@login_required
def managespace(parkingid):
    parking = models.Parking.get(models.Parking.id == parkingid)
    space_reservations = models.Reservation.select().where(models.Reservation.parking_id==int(parkingid))

    form=forms.ParkingForm()
    if form.validate_on_submit():
        parking.price = form.price.data
        parking.description = form.description.data
        parking.location = form.location.data
        parking.parkingPic = form.parkingPic.data
        parking.save()
        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('managespace.html', form=form, parking=parking, space_reservations=space_reservations)

@app.route('/editprofile/', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form=forms.UpdateProfile()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.fullname = form.fullname.data
        current_user.phoneNumber = form.phoneNumber.data
        current_user.address = form.address.data
        current_user.profileImgUrl = form.profileImgUrl.data
        current_user.carPic = form.carPic.data
        current_user.save()
        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('editprofile.html', form=form)

@app.route('/parking/<parkingid>/createreview', methods=['POST'])
@login_required
def createreview(parkingid):
    parking = models.Parking.get(models.Parking.id == parkingid)
    review_form = forms.ReviewForm()

    if review_form.validate_on_submit():
        models.Review.create(
            user=g.user._get_current_object(),
            content = review_form.content.data,
            parking = parking
        )

    return redirect('/parking/{}'.format(parkingid))

@app.route('/profile/review/<revid>/delete')
@login_required 
def delete_rev(revid):
    review = models.Review.get(models.Review.id == revid)
    review.delete_instance()

    return redirect(url_for('profilepage', username=g.user._get_current_object().username))

@app.route('/review/<revid>/edit', methods=['GET','POST'])
@login_required
def edit_rev(revid):
    review = models.Review.get(models.Review.id == revid)
    
    form = forms.ReviewForm()
    if form.validate_on_submit():
        review.content = form.content.data
        review.save()
        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('review.html', form=form, review=review)



if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username = 'Homer',
            email = 'homer@ga.com',
            fullname = 'Homer Simpson',
            password = '123',
            phoneNumber = '4151234567',
            address = '256 Anzavista ave, San Francisco',
            profileImgUrl = '',
            carPic = '',
            is_host = False
            )
        models.User.create_user(
            username = 'Ned',
            email = 'ned@ga.com',
            fullname = 'Ned Flanders',
            password = '123',
            phoneNumber = '4151234567',
            address = '573 8th ave, san francisco 94115',
            profileImgUrl = 'https://i.imgflip.com/acs9p.jpg',
            carPic = 'https://vignette.wikia.nocookie.net/simpsons/images/c/ca/NedsGeo.png/revision/latest?cb=20091222195711',
            is_host = False
            )
        models.Parking.create_parking(
            user = 1,
            price = '$25',
            description = 'OK parking space',
            location = '225 bush st san francisco',
            parkingPic = 'https://images.unsplash.com/14/unsplash_5243e9ef164a5_1.JPG?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
        )
        models.Parking.create_parking(
            user = 2,
            price = '$10',
            description = 'Friendly neighbors parking space',
            location = 'ocean beach san francisco',
            parkingPic = 'https://images.unsplash.com/photo-1465301055284-72f355cfd745?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
        )
        models.Parking.create_parking(
            user = 2,
            price = '$15',
            description = 'Safe parking space',
            location = 'sunset san francisco',
            parkingPic = 'https://images.unsplash.com/photo-1527377667-83c6c76f963f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60'
        )
        models.Reservation.create_res(
            user = 2,
            parking = 1,
            resDate = '5-5-19',
            duration = '1 day',
            carPic = 'http://fcauthority.com/wp-content/uploads/2017/01/Homers-Car-700x340.jpg'
        )
        models.Review.create_review(
            parking = 1,
            user = 2,
            content = 'Host were very pleasent'
        )
        models.Review.create_review(
            parking = 2,
            user = 1,
            content = 'Nice place.'
        )


    except ValueError:
        pass


    app.run(debug=DEBUG, port=PORT)