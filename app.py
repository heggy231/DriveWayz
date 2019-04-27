from flask import Flask, g, session
from flask import render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash
import os
import models 
import forms 
import json
import secrets

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
    models.User.create_user(
        username=form.username.data,
        email=form.email.data,
        password=form.password.data,
        fullname=form.fullname.data,
        phoneNumber=form.phoneNumber.data,
        address=form.address.data
    )
    return redirect(url_for('index'))

def handle_login(form):
    try:
        user = models.User.get(models.User.email == form.email.data)
    except models.DoesNotExist:
        flash("Your email or password doesn't match  ", "error")
    else:
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Hi! You have successfully Signed In!!!', 'success signin')
            return redirect(url_for('index'))
        else:
            flash("Your email or password doesn't match  ", "error")

def save_parking_picture(form_parking_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_parking_pic.filename)
    parking_pic_fn = random_hex + f_ext
    parking_picture_path = os.path.join(app.root_path, 'static/parking_pics', parking_pic_fn)
    form_parking_pic.save(parking_picture_path)

    return parking_pic_fn

def save_picture(form_profile_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_profile_pic.filename)
    profile_pic_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', profile_pic_fn)
    form_profile_pic.save(picture_path)

    return profile_pic_fn


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
    return redirect(url_for('index'))


@app.route('/parking/<parkingid>', methods=['GET','POST'])
def parking(parkingid):
    parking = models.Parking.get_by_id(int(parkingid))
    reviews = models.Review.select().where(models.Review.parking_id==int(parkingid))
    reservations = models.Reservation.select().where(models.Reservation.parking_id==int(parkingid))
    review_form = forms.ReviewForm()
    form = forms.ResForm()

    if form.validate_on_submit():
        models.Reservation.create(
            user=g.user._get_current_object(),
            resDate=form.resDate.data,
            parking=parking)

        return redirect(url_for('payment', parkingid=parking))

    return render_template('parkingspace.html', parking=parking, form=form, reviews = reviews, review_form=review_form, reservations=reservations)


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profilepage(username):
    user = models.User.get(models.User.username == username)
    parkings =  current_user.get_my_parkings()
    parking =  current_user.get_my_parkings()
    reservations = current_user.get_reservations()
    parking_form = forms.ParkingForm()
    reviews = current_user.get_my_reviews()
    profileImgUrl = url_for('static', filename='profile_pics/' + current_user.profileImgUrl )
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
        reservation.save()

        flash ('Your reservation has been updated!')
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
            location =form.location.data
        )
    return redirect(url_for('profilepage', username=g.user._get_current_object().username))

@app.route('/profile/<parkingid>/managespace', methods=['GET','POST'])
@login_required
def managespace(parkingid):
    parking = models.Parking.get(models.Parking.id == parkingid)
    space_reservations = models.Reservation.select().where(models.Reservation.parking_id==int(parkingid))

    form=forms.ParkingForm()
    if form.validate_on_submit():
        if form.parkingPic.data:
            parking_picture_file = save_parking_picture(form.parkingPic.data)
            parking.parkingPic = parking_picture_file
        parking.price = form.price.data
        parking.description = form.description.data
        parking.location = form.location.data
        parking.save()
        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('managespace.html', form=form, parking=parking, space_reservations=space_reservations)


@app.route('/editprofile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form=forms.UpdateProfile()
    if form.validate_on_submit():
        if form.profileImgUrl.data:
            picture_file = save_picture(form.profileImgUrl.data)
            current_user.profileImgUrl = picture_file
        if form.carPic.data:
            picture_file = save_picture(form.carPic.data)
            current_user.carPic = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.fullname = form.fullname.data
        current_user.phoneNumber = form.phoneNumber.data
        current_user.address = form.address.data
        current_user.save()

        flash('Your profile has been updated!', 'success')
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

        flash ('Your review has been updated!')
        return redirect(url_for('profilepage', username=g.user._get_current_object().username))

    return render_template('review.html', form=form, review=review)


@app.route('/payment/<parkingid>', methods=['GET'])
@login_required
def payment(parkingid):
    parking = models.Parking.get_by_id(int(parkingid))

    return render_template('payment.html',parking=parking)


if 'ON_HEROKU' in os.environ:
    print('hitting ')
    models.initialize()

if __name__ == '__main__':
    models.initialize()
    # try:
    #     models.User.create_user(
    #         username = 'Homer',
    #         email = 'homer@ga.com',
    #         fullname = 'Homer Simpson',
    #         password = '123',
    #         phoneNumber = '4151234567',
    #         address = '501 28th ave, San Francisco',
    #         profileImgUrl = '/samples/homer.jpg',
    #         carPic = 'samples/homercar.png'
    #     )
    #     models.User.create_user(
    #         username = 'Ned',
    #         email = 'ned@ga.com',
    #         fullname = 'Ned Flanders',
    #         password = '123',
    #         phoneNumber = '4151234567',
    #         address = '573 8th ave, san francisco 94115',
    #         profileImgUrl = '/samples/ned.png',
    #         carPic = 'samples/ned_car.png'
    #     )
    #     models.User.create_user(
    #         username = 'Alom',
    #         email = 'alom@ga.com',
    #         fullname = 'Alom Hossain',
    #         password = '123',
    #         phoneNumber = '4151234567',
    #         address = '256 Anzavista ave, san francisco 94115',
    #         profileImgUrl = '/samples/profile.png',
    #         carPic = 'samples/wrx.png'
    #     )
    #     models.User.create_user(
    #         username = 'AliW',
    #         email = 'aliw@ga.com',
    #         fullname = 'Ali Wong',
    #         password = '123',
    #         phoneNumber = '4151234567',
    #         address = '2210 23rd ave, san francisco 94115',
    #         profileImgUrl = '/samples/Ali_wong.jpg',
    #         carPic = 'samples/red_merc.jpg'
    #     )
    #     models.User.create_user(
    #         username = 'PeterG',
    #         email = 'peter@ga.com',
    #         fullname = 'Peter Griffin',
    #         password = '123',
    #         phoneNumber = '4151234567',
    #         address = '1834 Anza st, san francisco 94115',
    #         profileImgUrl = '/samples/peter.jpeg',
    #         carPic = 'samples/peter_griffin_car.png'
    #     )

    #     models.Parking.create_parking(
    #         user = 1,
    #         price = '$25',
    #         description = 'OK parking space',
    #         location = '225 bush st san francisco',
    #         parkingPic = 'samples/yellow_driveway.jpeg'
    #     )
    #     models.Parking.create_parking(
    #         user = 2,
    #         price = '$10',
    #         description = 'Friendly neighbors parking space',
    #         location = '573 8th ave, san francisco 94115',
    #         parkingPic = 'samples/old_house.jpeg'
    #     )
    #     models.Parking.create_parking(
    #         user = 2,
    #         price = '$15',
    #         description = 'Safe parking space',
    #         location = 'sunset san francisco',
    #         parkingPic = 'samples/mailbox.jpeg'
    #     )
    #     models.Parking.create_parking(
    #         user = 3,
    #         price = '$99',
    #         description = 'Gated Private Driveway',
    #         location = 'sunset san francisco',
    #         parkingPic = 'samples/gated_driveway.jpg'
    #     )
    #     models.Parking.create_parking(
    #         user = 5,
    #         price = '$1',
    #         description = 'Backalley - Dont Worry its safe.',
    #         location = '3rd and minna st',
    #         parkingPic = 'samples/back_alley.jpg'
    #     )
    #     models.Parking.create_parking(
    #         user = 4,
    #         price = '$55',
    #         description = 'Delightful Space',
    #         location = '2444 Greenwich St, San Francisco, CA 94123',
    #         parkingPic = 'samples/greenwich.png'
    #     )
    #     models.Parking.create_parking(
    #         user = 4,
    #         price = '$40',
    #         description = 'Kind owners and kind parking',
    #         location = '679 28th Ave, San Francisco, CA 94121',
    #         parkingPic = 'samples/28th.png'
    #     )
    #     models.Parking.create_parking(
    #         user = 1,
    #         price = '$35',
    #         description = 'Safe neighborhood driveway',
    #         location = '866 38th Ave, San Francisco, CA 94121',
    #         parkingPic = 'samples/38th.png'
    #     )
    #     models.Parking.create_parking(
    #         user = 3,
    #         price = '$20',
    #         description = 'Not Sketchy Area',
    #         location = '1226 48th Ave, San Francisco, CA 94122',
    #         parkingPic = 'samples/48th.png'
    #     )
    #     models.Parking.create_parking(
    #         user = 5,
    #         price = '$1000',
    #         description = 'Golden Driveway',
    #         location = '874 42nd Ave, San Francisco, CA 94121',
    #         parkingPic = 'samples/42nd.png'
    #     )

    #     models.Reservation.create_res(
    #         user = 1,
    #         parking = 2,
    #         resDate = '2019-05-05'
    #     )
    #     models.Reservation.create_res(
    #         user = 1,
    #         parking = 3,
    #         resDate = '2019-07-05'
    #     )
    #     models.Reservation.create_res(
    #         user = 2,
    #         parking = 1,
    #         resDate = '2019-06-05'
    #     )
    #     models.Reservation.create_res(
    #         user = 2,
    #         parking = 4,
    #         resDate = '2019-08-05'
    #     )
    #     models.Reservation.create_res(
    #         user = 3,
    #         parking = 3,
    #         resDate = '2019-09-05'
    #     )
    #     models.Reservation.create_res(
    #         user = 3,
    #         parking = 9,
    #         resDate = '2019-05-21'
    #     )
    #     models.Reservation.create_res(
    #         user = 4,
    #         parking = 10,
    #         resDate = '2019-03-010'
    #     )
    #     models.Reservation.create_res(
    #         user = 4,
    #         parking = 6,
    #         resDate = '2019-12-12'
    #     )
    #     models.Reservation.create_res(
    #         user = 5,
    #         parking = 8,
    #         resDate = '2019-04-010'
    #     )
    #     models.Reservation.create_res(
    #         user = 5,
    #         parking = 7,
    #         resDate = '2019-11-12'
    #     )

    #     models.Review.create_review(
    #         parking = 1,
    #         user = 2,
    #         content = 'Host were very pleasent'
    #     )
    #     models.Review.create_review(
    #         parking = 2,
    #         user = 1,
    #         content = 'Nice place.'
    #     )
    #     models.Review.create_review(
    #         parking = 4,
    #         user = 3,
    #         content = 'Area is nice, but smells funny.'
    #     )
    #     models.Review.create_review(
    #         parking = 5,
    #         user = 3,
    #         content = 'It reall is a back alley...'
    #     )
    #     models.Review.create_review(
    #         parking = 4,
    #         user = 4,
    #         content = 'This gated parking is perfect for when you want that added security. Would park here again despite the high price.'
    #     )
    #     models.Review.create_review(
    #         parking = 9,
    #         user = 2,
    #         content = 'Driveway not too sketchy at all,right near Golden Gate Park, dont have to walk too far.'
    #     )
    #     models.Review.create_review(
    #         parking = 10,
    #         user = 5,
    #         content = 'Host were very friendly and greeted me when I arrived and left.'
    #     )
    #     models.Review.create_review(
    #         parking = 1,
    #         user = 1,
    #         content = 'Whoops this is my parking space... thought it looked familiar.'
    #     )
    #     models.Review.create_review(
    #         parking = 1,
    #         user = 2,
    #         content = 'Oh homer.....'
    #     )
    #     models.Review.create_review(
    #         parking = 5,
    #         user = 3,
    #         content = 'This is a very cheap parking spot.'
    #     )
    #     models.Review.create_review(
    #         parking = 8,
    #         user = 4,
    #         content = 'Was able to book this spot in a pinch. Everything worked out well.'
    #     )
    #     models.Review.create_review(
    #         parking = 10,
    #         user = 5,
    #         content = 'Totally worth the $1000 I paid to park here!'
    #     ) 
    #     models.Review.create_review(
    #         parking = 10,
    #         user = 1,
    #         content = 'Who would actually park here?!'
    #     )
    #     models.Review.create_review(
    #         parking = 6,
    #         user = 2,
    #         content = 'Parking was hard to find and owners dont communicate well.'
    #     )
    #     models.Review.create_review(
    #         parking = 3,
    #         user = 4,
    #         content = 'Nice quiet neighborhood....kinda creepy.'
    #     )
    #     models.Review.create_review(
    #         parking = 7,
    #         user = 5,
    #         content = 'Owners where nice parking is small.'
    #     )


    # except ValueError:
    #     pass


    app.run(debug=DEBUG, port=PORT)