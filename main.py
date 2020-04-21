from flask import Flask, url_for, request, redirect, jsonify, json

from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user

from cassandra.cluster import Cluster

from flask import Blueprint

from passlib.apps import custom_app_context as pwd_context

from app import app



auth_api = Flask(__name__)

# User blueprint function to call another file

auth_api.register_blueprint(app)

auth_api.secret_key = 'CLOUD_SECRET_KEY'

login_manager = LoginManager(auth_api)


cluster = Cluster(contact_points=['172.17.0.2'],port=9042)

session = cluster.connect()


template_page = """

             <form action={} method='POST'>

             <input type='text' name='email' id='email' placeholder='email'/>

             <input type='password' name='password' id='password' placeholder='password'/>

             <input type='submit' name='submit'/>

             </form>

             """



class User(UserMixin):

    pass



# When a new user signs up

class Create:

    # Save username and hashed password in the database

    def new_user(self, name, password):

        password = self.hash_password(password)

        insert_cql = """INSERT INTO cloud.users (username, password_hash) VALUES

                    ('{}','{}');""".format(name,password)

        session.execute(insert_cql)


    # When a new user registers their details or existing user changes their password - hash input password and store it 

    def hash_password(self, password):

        password_hash = pwd_context.encrypt(password)

        return password_hash


# Save current user ID in flask_login

@login_manager.user_loader

def user_loader(email):

    user = User()

    user.id = email

    return user



# Home page display

@auth_api.route('/login', methods=['GET', 'POST'])

def login():

    if current_user.is_active:

        return "<h2>You are already logged in</h2>" + \
                "<a href='{}'>Home</a>".format(request.url_root), 201

    # Login page - user enters their username and password
    if request.method == 'GET':
        log_in_page = "<h2>Login</h2>" + template_page.format('login') + \
                    "<a href='{}newuser'>Sign Up</a>".format(request.url_root)
        return log_in_page
    log_in_page = "<h2>Log-in</h2>" + template_page.format('login') + \
                "<a href='{}newuser'>Sign Up</a>".format(request.url_root)
    email = request.form['email']
    ori_password = request.form['password']
    rows = session.execute("SELECT password_hash FROM cloud.users where username = %s LIMIT 1", ([email]))
    if not rows: #If the user enters a wrong or not existing username
        return ('<h2>This username does not exist. Please check your details.</h2>{}'.format(email,log_in_page)), 404
    elif pwd_context.verify(ori_password, rows[0].password_hash)==False:
        #If the user enters the wrong passoword
        return ('<h2>Invalid password. Please check your details and try again.</h2>{}'.format(log_in_page)), 404
    else:
        user = User()
        user.id = email #The user's email is their ID
        login_user(user) #Remember user id
        return ("""<h2>Welcome, {}
                </h2><a href='{}'>Home</a>""".format(current_user.id, request.url_root)), 201
   
    #When a new user signs up
    if request.method == 'POST': 
        email = request.json['email']
        ori_password = request.json['email']
        Create().new_user(email, ori_password)
        login_user(email)
        return ('<h1>Welcome, {}.</h1>'.format(email)) ,201 
    return 'Login error',404

# Logout page
@auth_api.route('/logout')
def logout():
    logout_user()
    return 'Logged out'

# Adding a new username and password to Cassandra 
@auth_api.route('/newuser', methods=['GET', 'POST'])
def new_user():
    sign_up_page = "<h2>Sign up</h2>" + template_page.format('newuser') + \
                    "<a href='{}login'>Login</a>".format(request.url_root)
    if request.method == 'GET':
        return sign_up_page
    email = request.form['email']
    ori_password = request.form['password']
    #If the chosen username already exists in the database
    rows = session.execute("SELECT * FROM cloud.users where username = %s ", ([email]))
    if rows:
        return ('<h1>username already exists</h1>'.format(email)), 404
    # Saving new username and hashed password into database
    Create().new_user(email, ori_password)
    user = User()
    user.id = email 
    login_user(user)
    return ("""<h2>Hello, {}</h2>
            <a href='{}'>Home</a>""".format(current_user.id, request.url_root)), 201
if __name__ == '__main__':
    auth_api.run(host='0.0.0.0',port=80)
