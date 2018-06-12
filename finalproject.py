from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import College, Base, CourseName, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Colleges Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///colleges.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# create a state token to request forgery.
# store it in the session for later validation


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_name' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(100))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is  connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 250px; height: 250px;\
    -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    session.close()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        session.close()
        # Reset the user's sesson.
        return redirect(url_for('showcolleges'))
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            flash("you have succesfully been logout")
        return redirect(url_for('showcolleges'))
    else:
        flash("you were not logged in")
        return redirect(url_for('showcolleges'))


# JSON APIs to view college Information
@app.route('/college/<int:college_id>/course/JSON')
def colleginfoJSON(college_id):
    session = DBSession()
    college = session.query(college).filter_by(id=college_id).one()
    courses = session.query(CourseName).filter_by(
        college_id=college_id).all()
    session.close()
    return jsonify(CourseNames=[i.serialize for i in items])


@app.route('/college/<int:college_id>/course/<int:course_id>/JSON')
def CourseinfoJSON(college_id, course_id):
    session = DBSession()
    Course_Name = session.query(CourseName).filter_by(id=course_id).one()
    session.close()
    return jsonify(Course_Name=Course_Name.serialize)


@app.route('/college/JSON')
def collegesJSON():
    session = DBSession()
    colleges = session.query(college).all()
    session.close()
    return jsonify(colleges=[r.serialize for r in colleges])


# Show all colleges
@app.route('/')
@app.route('/college/')
def showcolleges():
    session = DBSession()
    colleges = session.query(College).order_by(asc(College.name))
    session.close()
    return render_template('colleges.html', colleges=colleges)


@app.route('/college/<int:college_id>')
def collegeinfo(college_id):
    session = DBSession()
    college = session.query(College).filter_by(id=college_id).one()
    courses = session.query(CourseName).filter_by(
        college_id=college_id).all()
    session.close()
    return render_template('course.html', college=college, courses=courses)


@app.route('/college/<int:college_id>/course/<int:course_id>')
def courseinfo(college_id, course_id):
    session = DBSession()
    Course_Name = session.query(CourseName).filter_by(id=course_id).one()
    session.close()
    return jsonify(Course_Name=Course_Name.serialize)
# Create a new college


@app.route('/college/new/', methods=['GET', 'POST'])
def newcollege():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session = DBSession()
        newcollege = College(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newcollege)
        flash('New college %s Successfully Created' % newcollege.name)
        session.commit()
        session.close()
        return redirect(url_for('showcolleges'))
    else:
        return render_template('newcollege.html')

# Edit a college


@app.route('/college/<int:college_id>/edit/', methods=['GET', 'POST'])
def editcollege(college_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    editedcollege = session.query(
        College).filter_by(id=college_id).one()
    if creator.id != login_session['user_id']:
        flash("You cannot edit this college. This college belongs to % s"
              % creator.name)
        return redirect(url_for('showcolleges'))
    if request.method == 'POST':
        if request.form['name']:
            editedcollege.name = request.form['name']
            flash('college Successfully Edited %s' % editedcollege.name)
            session.commit()
            session.close()
            return redirect(url_for('showcolleges'))
    else:
        return render_template('editcollege.html', college=editedcollege)


# Delete a college
@app.route('/college/<int:college_id>/delete/', methods=['GET', 'POST'])
def deletecollege(college_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    collegeToDelete = session.query(
        College).filter_by(id=college_id).one()
    if creator.id != login_session['user_id']:
        flash("You cannot delete this college. This college belongs to %s"
              % creator.name)
        return redirect(url_for('showcolleges'))
    if request.method == 'POST':
        session.delete(collegeToDelete)
        flash('%s Successfully Deleted' % collegeToDelete.name)
        session.commit()
        session.close()
        return redirect(url_for('showcolleges', college_id=college_id))
    else:
        return render_template('deleteCollege.html', college=collegeToDelete)

# Show a college courses


@app.route('/college/<int:college_id>/')
@app.route('/college/<int:college_id>/course/')
def showCourses(college_id):
    session = DBSession()
    college = session.query(College).filter_by(id=college_id).one()
    courses = session.query(CourseName).filter_by(
        college_id=college_id).all()
    session.close()
    return render_template('course.html', courses=courses, college=college)


# Create a new course
@app.route('/college/<int:college_id>/course/new/', methods=['GET', 'POST'])
def newCourseName(college_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    college = session.query(College).filter_by(id=college_id).one()
    if request.method == 'POST':
        newcourse = CourseName(name=request.form['name'],
                               description=request.form['description'],
                               fee=request.form['fee'],
                               college_id=college_id, user_id=college.user_id)
        session.add(newcourse)
        session.commit()
        flash('New Course %s Name Successfully Created' % (newcourse.name))
        session.close()
        return redirect(url_for('showCourses', college_id=college_id))
    else:
        return render_template('newCourseName.html', college_id=college_id)

# Edit a course


@app.route('/college/<int:college_id>/course/<int:course_id>/edit',
           methods=['GET', 'POST'])
def editCourseName(college_id, course_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    editedCourse = session.query(CourseName).filter_by(id=course_id).one()
    college = session.query(College).filter_by(id=college_id).one()
    if creator.id != login_session['user_id']:
        flash("You cannot edit this college. This college belongs to %s"
              % creator.name)
        return redirect(url_for('showCourses'))
    if request.method == 'POST':
        if request.form['name']:
            editedCourse.name = request.form['name']
        if request.form['description']:
            editedCourse.description = request.form['description']
        if request.form['fee']:
            editedCourse.fee = request.form['fee']
        session.add(editedCourse)
        session.commit()
        flash('Course Name Successfully Edited')
        session.close()
        return redirect(url_for('showCourses', college_id=college_id))
    else:
        return render_template('editCourseName.html',
                               college_id=college_id, course_id=course_id,
                               course=editedCourse)


# Delete a course
@app.route('/college/<int:college_id>/course/<int:course_id>/delete',
           methods=['GET', 'POST'])
def deleteCourseName(college_id, course_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    college = session.query(College).filter_by(id=college_id).one()
    courseToDelete = session.query(CourseName).filter_by(id=course_id).one()
    if creator.id != login_session['user_id']:
        flash("You cannot delete this college. This college belongs to %s"
              % creator.name)
        return redirect(url_for('showCourses'))
    if request.method == 'POST':
        session.delete(courseToDelete)
        session.commit()
        flash('Course Name Successfully Deleted')
        session.close()
        return redirect(url_for('showCourses', college_id=college_id))
    else:
        return render_template('deleteCourseName.html', course=courseToDelete)


session.close()
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

