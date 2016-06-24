from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
# For database connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
# For the anti-forgery state token
import random
import string
# For connecting to google
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# JSON load for the CLIENT_ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu App" # This is the google project (Used the google project from the udacity tutorial)


# Database connection
engine = create_engine(
'sqlite:///itemcatalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods = ['POST'])
def gconnect():
    # Validate our anti-forgery token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If the anti-forgery token is valid, obtain the authorization code from google
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

    # Check if the user is already connected
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
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

    # see if user exists and if it does not add him to the database
    # if it does exist, simply add the id to the login_session

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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']

    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'Result is '
    print result

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    return render_template('category.html', categories = categories)

@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category_id)
    if 'username' not in login_session:
        return render_template('publicitem.html', category = category, items = items)
    else:
        return render_template('item.html', category = category, items = items)

@app.route('/category/<int:category_id>/items/new/', methods = ['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'GET':
        category = session.query(Category).filter_by(id = category_id).one()
        return render_template('newitem.html', category = category)
    elif request.method == 'POST':
        item = Item(name = request.form['name'], description = request.form['description'],
            category_id = category_id, user_id = login_session['user_id'])
        session.add(item)
        session.commit()
        flash("Item added successfully!")
        return redirect(url_for('showItems', category_id = category_id))

@app.route('/category/<int:category_id>/<int:item_id>/')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    itemCreator = getUserInfo(item.user_id)
    if 'username' not in login_session or login_session['user_id'] != itemCreator.id:
        return render_template('public_specific_item.html', item = item)
    else:
        return render_template('specific_item.html', item = item)

@app.route('/category/<int:category_id>/<int:item_id>/edit/', methods = ['GET', 'POST'])
def editItem(category_id, item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() { alert('You are not authorized to edit this item!');}</script><body onload = 'myFunction()'>"
    if request.method == 'GET':
        return render_template('edititem.html', item = item)
    elif request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()
        flash("Item edited successfully!")
        return redirect(url_for('showItem', category_id = category_id, item_id = item_id))

@app.route('/category/<int:category_id>/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(category_id, item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() { alert('You are not authorized to delete this item!');}</script><body onload = 'myFunction()'>"
    if request.method == 'GET':
        return render_template('deleteitem.html', item = item)
    elif request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item deleted successfully!")
        return redirect(url_for('showItems', category_id = category_id))

@app.route('/categories/JSON/')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(Category = [c.serialize for c in categories])

@app.route('/category/<int:category_id>/items/JSON/')
def itemsJSON(category_id):
    items = session.query(Item).filter_by(category_id = category_id)
    return jsonify(Item = [i.serialize for i in items])

@app.route('/category/<int:category_id>/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	return jsonify(Item = item.serialize)

# Helper methods

# Create a user based on the information given by a login_session
# The login_session is created when you log in via google plus.
def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'],
                picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).first()
    return user.id

# Given a user id, this method returns the user
def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

# Given an email, it returns a user id if that user is in our db
def getUserID(email):
    try:
        user = session.query(User).filter_by(id = user_id).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = "my_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)
