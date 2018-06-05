from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, carmodel, modelcategory, User
from flask import session as login_session
import random, string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
from functools import wraps
import httplib2
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Lamborghini models"

#connect to Database
engine = create_engine('sqlite:///carmodel.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# anti-forgery state token
@app.route('/login')
def showlogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in  xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        #upgrade authorization code in a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there is an error in the access token, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify access token is for intended user.
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

    # Check user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt' : 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists and make new one if they don't
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
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User helper functions
def createUser(login_session):
    newUser = User(
            name=login_session['username'],
            email=login_session['email'],
            picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
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
           

# Disconnect - revoke a current user's token
@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # token given is invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


    # User helper functions
    def getUserID(email):
        try:
            user = session.query(User).filter_by(email=email).one()
            return user.id
        except:
            return None


    def getUserInfo(user_id):
        user = session.query(User).filter_by(id=user_id).one()
        return user


    def createUser(login_session):
        newUser = User(
            name=login_session['username'],
            email=login_session['email'],
            picture=login_session['picture'])
        session.add(newUser)
        session.commit()
        user = session.query(User).filter_by(email=login_session['email']).one()
        return user.id


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            if 'gplus_id' in login_session:
                del login_session['gplus_id']
            if 'credentials' in login_session:
                del login_session['credentials']
        flash("You have successfully been logged out.", 'success')
        return redirect(url_for('showmodel'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showmodel'))

# JSON Api's for viewing car models

@app.route('/model/JSON')
def modelsJSON():
    models = session.query(carmodel).all()
    return jsonify(models=[r.serialize for r in models])

@app.route('/model/<string:car_name>/category/JSON')
def carmodelJSON(car_name):
    model = session.query(carmodel).filter_by(id=car_name).one_or_none()
    category = session.query(modelcategory).filter_by(
           car_name=car_name).all()
    return jsonify(modelcategory=[i.serialize for i in category])
  
@app.route('/model/<string:car_name>/category/<string:car_model>/JSON')
def modelcategoryJSON(car_name, car_model):
    model_category = session.query(modelcategory).filter_by(id=car_model).one_or_none()
    return jsonify(model_category=model_category.serialize)
    
# Crud and routing
#__________________

# show car models
@app.route('/')
@app.route('/model')
def showmodel():
    models = session.query(carmodel).all()
    if 'username' not in login_session:
        return render_template('publicmodel.html', models=models)
    else:
        return render_template('model.html', models=models)

# add a new model
@app.route('/model/new', methods=['GET', 'POST'])
def newmodel():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newmodel = carmodel(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newmodel)
        session.commit()
        flash('New model %s Successfully added' % newmodel.name)
        return redirect(url_for('showmodel'))
    else:
        return render_template('newmodel.html')

# edit car model
@app.route('/model/<string:car_name>/edit', methods=['GET', 'POST'])
def editmodel(car_name):
    if 'username' not in login_session:
        return redirect('/login')
    editmodel = session.query(carmodel).filter_by(id=car_name).one_or_none()
    if request.method == 'POST':
        if request.form['name']:
            editmodel.name = request.form['name']
            flash('car model has been edited %s' % editmodel.name)
            return redirect(url_for('showmodel'))
    else:
        return render_template('editmodel.html', model=editmodel)

# delete car model
@app.route('/model/<string:car_name>/delete', methods=['GET', 'POST'])
def deletemodel(car_name):
    deletemodel = session.query(carmodel).filter_by(id=car_name).one_or_none()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(deletemodel)
        session.commit()
        flash('%s Successfully Deleted' % deletemodel.name)
        return redirect(url_for('showmodel', car_name=car_name))
    else:
        return render_template('deletemodel.html', model=deletemodel)


# show category of the car models
@app.route('/model/<string:car_name>/model/<string:car_model>/category')
def showclass(car_name, car_model):
    model = session.query(carmodel).filter_by(id=car_name).one_or_none()
    category = session.query(modelcategory).filter_by(car_name=car_name).all()
    return render_template('category.html', category=category, model=model)


# add new car model category
@app.route('/model/<string:car_name>/category/new', methods=['GET', 'POST'])
def addclass(car_name):
    if 'username' not in login_session:
        return redirect('/login')
    model = session.query(carmodel).filter_by(id=car_name).one_or_none()
    if request.method == 'POST':
        newcategory = modelcategory(name=request.form['name'], description=request.form['description'],
        classification=request.form['classification'], car_name=car_name)
        session.add(newcategory)
        session.commit()
        flash('New category %s successfully added' % (newcategory.name))
        return redirect(url_for('showmdodelcategory', car_name=car_name))
    else:
        return render_template('newcategory.html',car_name=car_name)

# edit car model category
@app.route('/model/<string:car_name>/category/<string:car_model>/edit', methods=['GET', 'POST'])
def editclass(car_name, car_model):
    if 'username' not in login_session:
        return redirect('/login')
    editcategory = session.query(modelcategory).filter_by(id=car_model).one_or_none()
    model = session.query(carmodel).filter_by(id=car_name).one_or_none()
    if request.method == 'POST':
        if request.form['name']:
            editcategory.name = request.form['name']
        if request.form['description']:
            editcategory.description = request.form['description']
        if request.form['classification']:
            editcategory.classification = request.form['classification']
            session.add(editcategory)
            session.commit()
            flash('Category successfully edited')
            return redirect(url_for('showclass', car_name=car_name))
    else:
        return render_template('editcategory.html', car_name=car_name, car_model=car_model, category=editcategory)


# delete car model-category
@app.route('/model/<string:car_name>/category/<string:car_model>/delete', methods=['GET', 'POST'])
def deleteclass(car_name, car_model):
    if 'username' not in login_session:
        return redirect('/login')
    model = session.query(carmodel).filter_by(id=car_name).one_or_none()
    deletecategory = session.query(modelcategory).filter_by(id=car_model).one_or_none()
    if request.method == 'POST':
        session.delete(deletecategory)
        session.commit()
        flash('Category has been deleted')
        return redirect(url_for('showclass', car_name=car_name))
    else:
        return render_template('deletecategory.html', category=deletecategory)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)

