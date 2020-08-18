from flask import  render_template,request,session,redirect,abort
from passlib.hash import sha256_crypt
import os
from application import app, mysql
from flask_mysqldb import MySQL
from dotenv import load_dotenv,find_dotenv
from application.db.db import * #import everything from the db module

load_dotenv(find_dotenv('.env')) #finds the .env file


@app.route('/getdata') #route to test the database
def data():
    con = mysql.connection
    cursor = con.cursor()
    #cursor.execute("INSERT INTO testinguser (firstname, lastname) VALUES ('yaosheng', 'xu');")
    #con.commit()
    cursor.execute('SELECT * FROM USER;') #get all the data from the user table

    rv = cursor.fetchall()
    # session['user'] = rv[1]
    return str(rv)

@app.route('/home')
@app.route("/") #route to the home page
def home():
    exist = None
    if 'user' not in session: # if 'user' does not exist in session, then declare with None value
        session['user'] = None
    if session['user'] is not None:
        exist = session['user']
        print(exist)
    return render_template("index.html",user=exist)

@app.route("/userhome/") #route to the account home page
def userhome():
    #get the user object from the session
    if not check_if_user_is_logged_in(): #if the user is not logged in then they don't have access to this page
        return redirect('/')
    else: #if user does exist, get the user's firstname from the session
        user = session.get('user')
        wishlist = get_the_users_wishlist(session.get('id')) #get the wishlist from the database to determine if the user has one
    return render_template("user/account.html",user=user,wishlist=wishlist)

@app.route("/shoppingcart/")
def shoppingcart():
    return render_template("shoppingcart.html")

@app.route("/signout/") #route to sign out the account
def signout():
    session.clear()
    print(session)
    return redirect("/")

@app.route("/register/") #route to the register page
def register():
    try:
        if session['user'] is not None: #if user exist, then go to the user's account page
            return redirect('/userhome/')
    except KeyError as e:
        print(e)
    return render_template("register.html")

@app.route("/signup/", methods=['POST']) #route to sign up the account
def signup():
    if request.method == 'POST':
        con = mysql.connection
        cursor = con.cursor()
        email = request.form.get('Email')
        firstname = request.form.get('Firstname')
        lastname = request.form.get('Lastname')
        setPassword = request.form.get('Passwords')
        hashPassword = sha256_crypt.hash(setPassword)
        #Check if the user exist
        if cursor.execute("SELECT * FROM USER WHERE Email LIKE %s", [email]):
            existError = "Email already exist"
            return render_template("register.html", existError=existError)

        #insert new user information into user table
        cursor.execute("INSERT INTO USER (Firstname, Lastname, Email, Passwords) VALUES (%s, %s, %s, %s)",
        (firstname, lastname, email, hashPassword))
        con.commit()
        return redirect('/register/')


@app.route("/login/", methods=['POST']) #route to the register page
def login():
    if request.method == 'POST':
        con = mysql.connection
        cursor = con.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        #query the database for user table by the username
        #select * from user where username = 'username'
        #if user does exist, then compare the password
        if cursor.execute("SELECT * FROM USER WHERE Email LIKE %s", [username]):
            rv = cursor.fetchone()
            if sha256_crypt.verify(password, rv[4]):
                #if the user exist and password matches then login succuess
                session['id'] = rv[0]
                session['user'] = rv[1]
                session['email'] = rv[3]
                session['password'] = rv[4]
                return redirect('/userhome/')
            else:
                loginError = "Enter the valid Email or Password"
        else:
            loginError = "Enter the valid Email or Password"
        return render_template("register.html", loginError=loginError)

@app.route('/personal/') #route to the user's personal settings page
def personal_details():
    #get the user object from the session
    if 'user' not in session or session['user'] == None: #if the user is not logged in then they don't have access to this page
        return redirect('/')
    return render_template('user/personaldetails.html')

@app.route('/change_personal_detail/', methods=['POST']) #route to change personal detail
def change_personal_detail():

    if request.method == 'POST':
        con = mysql.connection
        cursor = con.cursor()
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        if firstname:
            cursor.execute("UPDATE USER SET Firstname = %s WHERE Email = %s", (firstname, session['email']))
            session['user'] = firstname

        if lastname:
            cursor.execute("UPDATE USER SET Lastname = %s WHERE Email = %s", (lastname, session['email']))

        con.commit()

    return redirect('/personal/')

@app.route('/change_password/', methods=['POST']) #route to change password
def change_password():
    if request.method == 'POST':
        con = mysql.connection
        cursor = con.cursor()

        currentPass = request.form.get('currentpass')
        newPassword = request.form.get('newpassword')
        hashNewPassword = sha256_crypt.hash(newPassword)

        if sha256_crypt.verify(currentPass, session['password']):
            cursor.execute("UPDATE USER SET Passwords = %s WHERE Email = %s", (hashNewPassword, session['email']))
        con.commit()
    return redirect('/userhome/')

@app.route('/payment-methods/') #route to the user's payment page
def payment_methods():
    #get the user object from the session
    if 'user' not in session or session['user'] == None: #if the user is not logged in then they don't have access to this page
        return redirect('/')
    return render_template('user/paymentmethod.html')


# All route for user to access Clothing
@app.route('/items/clothing/bottom/') #route to the user to access clothing bottom
def items_bottom():
    con = mysql.connection
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Item WHERE Subcategories = 'bottom'")
    item = cursor.fetchall()

    return render_template('item/clothing/bottom.html',item=item)


@app.route('/items/clothing/dresses/') #route to the user to access clothing dresses
def items_dresses():
    con = mysql.connection
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Item WHERE Subcategories = 'dresses'")
    item = cursor.fetchall()

    return render_template('item/clothing/dresses.html',item=item)

@app.route('/items/clothing/suits/') #route to the user to access suits
def items_suits():
    con = mysql.connection
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Item WHERE Subcategories = 'suits'")
    item = cursor.fetchall()

    return render_template('item/clothing/suits.html',item=item)

@app.route('/items/clothing/tops/') #route to the user to access tops
def items_tops():
    con = mysql.connection
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Item WHERE Subcategories = 'top'")
    item = cursor.fetchall()

    return render_template('item/clothing/tops.html',item=item)


@app.route('/user/wishlist/') #route to the wishlist, ONLY logged in user can access their wishlist
def wishlist_view():
    if check_if_user_is_logged_in():
        wishlist = get_the_users_wishlist(session['id']) #get the list of the user's wishlist, pass in the users id
        print(wishlist)
        return render_template('user/wishlist.html',wishlist=wishlist)
    return redirect('/register/')

@app.route('/user/wishlist/<category>/<subcategory>/<int:id>') #route to add the item to wishlist
def add_to_wishlist(category,subcategory,id): #pass in the cat,and subcat, to redirect to the right page, and id reference item
    if check_if_user_is_logged_in():
        add_item_to_wishlist(session['id'],id) #pass in the user id and the item id
        return redirect('/items/{}/{}'.format(category,subcategory))
    return '<h1>401- Unauthorized- Access is Denied</h1>', 401 #if user is not signed in, they don't have access to this route

@app.route('/user/wishlist/delete/<int:id>') #route to delete an item from the user's wishlist, pass in the item id
def delete_from_wishlist(id):
    if check_if_user_is_logged_in(): #check if the user is logged in
        delete_item_from_wish_list(session['id'],id) #pass in the user id and the item id
        return redirect('/user/wishlist/')
    return '<h1>401- Unauthorized- Access is Denied</h1>', 401 #if user is not signed in, they don't have access to this route


def check_if_user_is_logged_in(): #function to check if the user is logged in
    try:
        if 'user' in session and session['user'] is not None:
            return True
    except KeyError: #catch if there is a KeyError, there is an error that means that the 'user' does not exist
        return False
    return False
