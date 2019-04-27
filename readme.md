1) postGresql steps: https://git.generalassemb.ly/sf-wdi-51/psql-install-intro
2) heroku steps: https://git.generalassemb.ly/sf-wdi-51/flask-deployment
# DriveWayz

### What is DriveWayz?
  Think Airbnb but for driveways. DriveWayz is an app to rent peoples driveways to park your car, or owners can rent out their own driveway to make money.

### Motivation
A friend of mine suggested the idea because she lives near Golden Gate Park and sees tons of people looking for parking whenever they have large events in the park. 

### Technologies Used
Python, Flask, WTForms, Peewee, SQLite3, Bootstrap, Custom CSS

### External APIs
- Google Maps API
- Stripe Payment API

### Wireframes of early design ideas
#### Login page
![Screenshot of wireframe](../master/assets/wireframe1.png)
#### User Pages
![Screenshot of wireframe](../master/assets/wireframe2.png)
![Screenshot of wireframe](../master/assets/wireframe3.png)
#### Listings of parking spaces with map
![Screenshot of wireframe](../master/assets/wireframe4.png)

### Entitiy Relationship Diagram of database tables
I had 4 database tables, a User, Parking, Reservations, and Reviews
![Screenshot of erd](../master/assets/ERD.jpg)

### Code snippets of code that I am proud of
Uploading a picutre by defining a save path function outside of a route function
![Screenshot of code](../master/assets/code1.png)
![Screenshot of code](../master/assets/code2.png)
User profile page, this is like a hub of all database tables with almost all crud functionality all in one page.
![Screenshot of code](../master/assets/code3.png)

### Challenges
- Getting multiple form.validate_on_submit in one route
- Accessing referenced data from one table through another table
- Setting a default image and uploading a picture to replace it
- Sending the correct error when double booking a reservation
