
from flask import Flask, render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
SCHEMA = 'users_db' 

app = Flask(__name__)
app.secret_key = "1234"
bcrypt = Bcrypt(app)

#display all the users. 
@app.route('/users', methods=['GET'])
def index():
  mysql = connectToMySQL("users_db")
  users = mysql.query_db("SELECT * FROM users")
  return render_template('success.html', email_addresses = users) #pass location list to the index.html page

#display a form allowing users to create a new user.
@app.route('/users/new')   
def new():
  return render_template('index.html') 

#display the info for a particular user with given id.
@app.route('/users/id/<userid>')
def show(userid):


    database = connectToMySQL(SCHEMA)
    query = "SELECT * FROM users WHERE id = " + userid
    data = {
            'id': userid
        }
    user_id = database.query_db(query, data)
    first_name = user_id[0]['first_name']
    last_name = user_id[0]['last_name']
    email = user_id[0]['email']
    created_at = user_id[0]['created_at']
    return render_template('user.html', id=userid, first_name=first_name, last_name=last_name, email=email, created_at=created_at, selecteduser = user_id) #looping through selected user on html page. can also just use id = user_id[0]['id']

#remove a particular user with the given id.
@app.route('/users/<userid>/destroy')
def destroy(userid):
    database = connectToMySQL(SCHEMA)
    query = "DELETE FROM users_db.users WHERE (`id` = '" + userid + "');"
    data = {
            'id': userid
        }
    user_id = database.query_db(query, data)
    return redirect('/users')

#route is from the update button on the edit user page
@app.route('/users/update/<userid>', methods=['POST'])
def update(userid):
    print("update button is working")
    print(userid)
    db = connectToMySQL(SCHEMA) #connect to DB

    query = 'UPDATE users SET email = %(email)s, first_name = %(first_name)s, last_name = %(last_name)s WHERE (id = %(id)s);' #query DB

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'id': userid
    }
    print(data)
    user_id = db.query_db(query, data)
    mysql = connectToMySQL("users_db")

    return redirect('/users')

# display a form allowing users to edit an existing user with the given id. 
@app.route('/users/<userid>/edit') #<  userid >  is a variable
def edit(userid):
    print("Edit button is working")

    return render_template('edit.html', userid = userid)

#CREATE USERS
@app.route('/users/create', methods=['POST'])
def create():
  errors = False


  # check if email is valid
    # if so, check for uniqueness
  if not EMAIL_REGEX.match(request.form['email']): # if email isn't valid, using the regex 
    flash("Email must be valid")
    errors = True
  db = connectToMySQL(SCHEMA) #connect to database
  query = 'SELECT id FROM users WHERE email = %(email)s;'  #query database, and inject %(email)s;
  data = {
    'email': request.form['email']  
  }
  matching_users = db.query_db(query, data)#test for matching users
  if len(matching_users) > 0:
    flash("Email already in use")
    errors = True

  if errors == True:
    return render_template('index.html') 
  else:
    # add informattion to database
    db = connectToMySQL(SCHEMA) #connect to DB
    query = 'INSERT INTO users (email, first_name, last_name, created_at, updated_at) VALUES(%(email)s, %(first_name)s, %(last_name)s, NOW(), NOW())'#insert these values into the DB
    data = {
      'email': request.form['email'],
      'first_name': request.form['first_name'],
      'last_name': request.form['last_name']
    }
    user_id = db.query_db(query, data)
    mysql = connectToMySQL("users_db")
    users = mysql.query_db("SELECT * FROM users")
    # return render_template('success.html', email_addresses = users, current_email = session.email)
    ##### adding, to confirm this works:
    return redirect('/users') #do i need to add the above?

if __name__ == "__main__":
  app.run(debug=True)