from flask import Flask, flash, jsonify, redirect, render_template, request, session
# from flask_mysql_connector import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import os
import urllib.parse


import psycopg2

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cs50'


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mysql = MySQL(app)


app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://hqqhtuffmqljby:5cc09d4520f486d103b430375213b45f3892114d81e9e9ade28e4129eda13eb4@ec2-3-215-207-12.compute-1.amazonaws.com:5432/daeased18jut3h'


db = SQLAlchemy(app)

pg_conn = psycopg2.connect(
    database="daeased18jut3h", user="hqqhtuffmqljby", password="5cc09d4520f486d103b430375213b45f3892114d81e9e9ade28e4129eda13eb4", host="ec2-3-215-207-12.compute-1.amazonaws.com", port="5432"
)

pg_cursor = pg_conn.cursor()


class Appliances(db.Model):
    __tablename__ = 'appliances'
    app_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(200))
    type = db.Column(db.String(200))
    power = db.Column(db.Float)
    duration = db.Column(db.Float)
    frequency = db.Column(db.String(200))
    daily_usage = db.Column(db.Float)
    monthly_usage = db.Column(db.Float)
    daily_cost = db.Column(db.Float)
    monthly_cost = db.Column(db.Float)

    def __init__(self, user_id, name, type, power, duration, frequency, daily_usage, monthly_usage, monthly_cost, daily_cost):
        self.user_id = user_id
        self.name = name
        self.type = type
        self.power = power
        self.duration = duration
        self.frequency = frequency
        self.daily_usage = daily_usage
        self.monthly_usage = monthly_usage
        self.daily_cost = daily_cost
        self.monthly_cost = monthly_cost


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    cost_limit = db.Column(db.Float, default=1000)

    def __init__(self, name, email, password, cost_limit):
        self.name = name
        self.email = email
        self.password = password
        self.cost_limit = cost_limit


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=["POST"])
def login():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        email = request.form.get('email')
        password= request.form.get('password')
        
        pg_cursor.execute("SELECT * from users WHERE email = %s", [email])
        user = pg_cursor.fetchall()

        if len(user) <= 0 or not check_password_hash(user[0][3], password):
            return redirect('/')
        
        session['user_id'] = user[0][0]

        pg_cursor.execute("SELECT * from appliances WHERE user_id = %s", [user[0][0]])
        x = pg_cursor.fetchall()

        if len(x) > 0:
            session['isLimitSet'] = 1
        # Redirect user to home page
        return redirect('/home')


@app.route('/')
def index():
    if session.get('user_id') is None:
        return render_template('index.html')
    else:
        return redirect('/home')


@app.route('/home')
@login_required
def home():
    pg_cursor.execute("SELECT * from users WHERE user_id = %s", [session.get('user_id')])
    user = pg_cursor.fetchall()

    if session.get('isLimitSet') is None:
        wasSet = 0
    else:
        wasSet = 1
    
    pg_cursor.execute("SELECT * from appliances WHERE user_id = %s", [session.get('user_id')])
    apps = pg_cursor.fetchall()

    length = len(apps)

    mtotal = 0
    entertainment_block = 0
    lighting_block = 0
    cooling_block = 0
    kitchen_block = 0
    household_block = 0

    
    daily_cost = 0
    monthly_cost = 0
    daily_usage = 0
    monthly_usage = 0
    for app in apps:
        daily_usage += app[7]
        monthly_usage += app[8]
        daily_cost += app[9]
        monthly_cost += app[10]

        if app[3] == "Cooling":
            cooling_block += app[8]
        elif app[3] == "Lighting":
            lighting_block += app[8]
        elif app[3] == "Entertainment":
            entertainment_block += app[8]
        elif app[3] == "Kitchen Appliances":
            kitchen_block += app[8]
        else:
            household_block += app[8]

        
    
    daily_cost = round(daily_cost, 2)
    monthly_cost = round(monthly_cost, 2)
    daily_usage = round(daily_usage, 2)
    monthly_usage = round(monthly_usage, 2)

    error = 0
    if monthly_cost > user[0][4]:
        error = 1
    
    
    if monthly_usage != 0:
        pmt1 = f"{entertainment_block / monthly_usage * 100}%"
        pmt2 = f"{lighting_block / monthly_usage * 100}%"
        pmt3 = f"{cooling_block / monthly_usage * 100}%"
        pmt4 = f"{kitchen_block / monthly_usage * 100}%"
        pmt5 = f"{household_block / monthly_usage * 100}%"
    else:
        pmt1 = 0
        pmt2 = 0
        pmt3 = 0
        pmt4 = 0
        pmt5 = 0


    outer_holder = monthly_cost / user[0][4] * 100
    if outer_holder < 100:
        actual_limit = f"{outer_holder}%"
    else:
        error = 1
        actual_limit = "100%"
    print(outer_holder)




    return render_template('home.html', user = user, wasSet = wasSet, 
                            apps = apps, length = length, d_cost = daily_cost, m_cost = monthly_cost, 
                            d_usage = daily_usage, m_usage = monthly_usage, error = error, pmt1 = pmt1, 
                            pmt2 = pmt2, pmt3 = pmt3, pmt4 = pmt4, pmt5 = pmt5, actual_limit = actual_limit)


@app.route('/add', methods=["POST"])
def add():
    name = request.form.get('name')
    app_type = request.form.get('type')
    duration = request.form.get('duration')
    frequency = request.form.get('frequency')
    power = request.form.get('power')
    user_id = session.get('user_id')

    if app_type is None or frequency is None:
        return redirect('/')

    if frequency == "Daily":
        factor = 30
        days = 1
    elif frequency == "Weekly":
        factor=  4
        days = 7
    else:
        factor = 1
        days = 30

    daily_usage = round(float(power) * float(duration) / float(days) / 1000, 2)
    monthly_usage = round(float(factor) * float(power) /1000 * float(duration), 2)
    daily_cost = round(daily_usage * 11.32, 2)
    monthly_cost = round(monthly_usage * 11.32, 2)
    


    pg_cursor.execute("INSERT INTO appliances (user_id, name, type, power, frequency, duration, daily_usage, monthly_usage, daily_cost, monthly_cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [user_id, name, app_type, power, frequency, duration, daily_usage, monthly_usage, daily_cost, monthly_cost])
    pg_conn.commit()
    
    return redirect('/')


@app.route('/delete', methods=["POST"])
def delete():
    app_id = request.form.get('app_id')

    pg_cursor.execute("DELETE FROM appliances WHERE app_id = %s", [app_id])
    pg_conn.commit()
    return redirect('/')


@app.route('/setlimit', methods=["POST"])
def setlimit():
    cost_limit = request.form.get('cost_limit')
    pg_cursor.execute("UPDATE users SET cost_limit = %s WHERE user_id = %s", [cost_limit, session.get('user_id')])
    pg_conn.commit()
    session['isLimitSet'] = 1
    return redirect('/')


@app.route('/signup', methods=["POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')


       

        pg_cursor.execute("INSERT INTO users (name, email, password, cost_limit) VALUES (%s, %s, %s, '1000')", [name, email, generate_password_hash(password)])
        pg_conn.commit()

        # cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, generate_password_hash(password)))
        # mysql.connection.commit()
        return redirect('/')
        
        
@app.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect('/')


@app.route('/update', methods=["POST"])
def update():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    if password != confirm:
        return redirect('/')
    
    pg_cursor.execute("UPDATE users SET name = %s, email = %s, password = %s WHERE user_id = %s", [name, email, generate_password_hash(password), session.get('user_id')])
    pg_conn.commit()

    return redirect('/')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template('apology.html')


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)







