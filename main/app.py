from flask import Flask, render_template,request,session,redirect
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import os
from dotenv import load_dotenv,find_dotenv

app = Flask(__name__)
mysql = MySQL(app)

load_dotenv(find_dotenv('.env')) #finds the .env file

#set up the database configurations
app.config['MYSQL_HOST'] = os.getenv('HOST')
app.config['MYSQL_USER'] = os.getenv('USER')
app.config['MYSQL_PASSWORD'] = os.getenv('PASS')
app.config['MYSQL_DB'] = os.getenv('DB')
app.config['MYSQL_PORT'] = int(os.getenv('PORT'))

@app.route('/getdata') #route to test the database
def data():
    con = mysql.connection
    cursor = con.cursor()
    #cursor.execute("INSERT INTO testinguser (firstname, lastname) VALUES ('yaosheng', 'xu');")
    #con.commit()
    cursor.execute('SELECT * FROM USER;') #get all the data from the user table

    rv = cursor.fetchone()
    session['user'] = rv[1]
    return str(rv[1])

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

@app.route("/userhome/") #route to the home page
def userhome():
    #get the user object from the session
    if 'user' not in session or session['user'] == None: #if the user is not logged in then they don't have access to this page
        return redirect('/')
    else: #if user does exist, get the user's firstname from the session
        user = session.get('user')

    return render_template("user/account.html",user=user)

@app.route("/signout/")
def signout():
    session.clear()
    print(session)
    return redirect("/")

@app.route("/register/") #route to the register page
def register():
    if session['user'] is not None:
        return redirect('/userhome/')
    return render_template("register.html")

@app.route("/signup/", methods=['POST'])
def signup():
    con = mysql.connection
    cursor = con.cursor()
    if request.method == 'POST':
        email = request.form.get('Email')
        firstname = request.form.get('Firstname')
        lastname = request.form.get('Lastname')
        setPassword = request.form.get('Passwords')
        hashPassword = sha256_crypt.hash(setPassword)
        #Check if the user exist
        if cursor.execute("SELECT * FROM USER WHERE Email LIKE %s", [email]):
            return render_template("error.html")

        #insert new user information into user table
        cursor.execute("INSERT INTO USER (Firstname, Lastname, Email, Passwords) VALUES (%s, %s, %s, %s)",
        (firstname, lastname, email, hashPassword))
        con.commit()
        return redirect('/register/')


@app.route("/login/", methods=['POST']) #route to the register page
def login():
    con = mysql.connection
    cursor = con.cursor()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        #query the database for user table by the username
        #select * from user where username = 'username'
        #if user does exist, then compare the password
        if cursor.execute("SELECT * FROM USER WHERE Email LIKE %s", [username]):
            rv = cursor.fetchone()
            if sha256_crypt.verify(password, rv[4]):
                #if the user exist and password matches then login succuess
                session['user'] = rv[1]
                session['email'] = rv[3]
                return redirect('/userhome/')
        return render_template("error.html")

@app.route('/personal/') #route to the user's personal settings page
def personal_details():
    print(session)
    return render_template('user/personaldetails.html')

@app.route('/change_personal_detail/', methods=['POST'])
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

@app.route('/payment-methods/') #route to the user's payment page
def payment_methods():
    return render_template('user/paymentmethod.html')


if __name__ == "__main__":
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.run(debug=True)
