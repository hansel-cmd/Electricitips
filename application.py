from flask import Flask, flash, jsonify, redirect, render_template, request, session
# from flask_mysql_connector import MySQL
from flask_mysqldb import MySQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import os
import urllib.parse
import psycopg2
import urlparse

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'cs50'

app.config['MYSQL_HOST'] = 'ec2-3-215-207-12.compute-1.amazonaws.com'
app.config['MYSQL_USER'] = 'hqqhtuffmqljby'
app.config['MYSQL_PASSWORD'] = '5cc09d4520f486d103b430375213b45f3892114d81e9e9ade28e4129eda13eb4'
app.config['MYSQL_DB'] = 'daeased18jut3h'
app.config['DATABASE_URI'] = 'postgres://hqqhtuffmqljby:5cc09d4520f486d103b430375213b45f3892114d81e9e9ade28e4129eda13eb4@ec2-3-215-207-12.compute-1.amazonaws.com:5432/daeased18jut3h'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# mysql = MySQL(app)
result = urlparse.urlparse("postgres://hqqhtuffmqljby:5cc09d4520f486d103b430375213b45f3892114d81e9e9ade28e4129eda13eb4@ec2-3-215-207-12.compute-1.amazonaws.com:5432/daeased18jut3h")
un = result.username
pw = result.password
db = result.path[1:]
hn = result.hostname
mysql = psycopg2.connect(user=un, password=pw, host=hn, database=db)




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
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from users WHERE email = %s", [email])
        user = cur.fetchall()
        cur.close()

        if len(user) <= 0 or not check_password_hash(user[0][3], password):
            return redirect('/')
        
        session['user_id'] = user[0][0]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * from appliances WHERE user_id = %s", [user[0][0]])
        x = cur.fetchall()

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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from users WHERE user_id = %s", [session.get('user_id')])
    user = cur.fetchall()
    cur.close()

    if session.get('isLimitSet') is None:
        wasSet = 0
    else:
        wasSet = 1
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from appliances WHERE user_id = %s", [session.get('user_id')])
    apps = cur.fetchall()
    cur.close()

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
    


    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO appliances (user_id, name, type, power, frequency, duration, daily_usage, monthly_usage, daily_cost, monthly_cost) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [user_id, name, app_type, power, frequency, duration, daily_usage, monthly_usage, daily_cost, monthly_cost])
    mysql.connection.commit()
    
    return redirect('/')


@app.route('/delete', methods=["POST"])
def delete():
    app_id = request.form.get('app_id')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM appliances WHERE app_id = %s", [app_id])
    mysql.connection.commit()
    return redirect('/')


@app.route('/setlimit', methods=["POST"])
def setlimit():
    cost_limit = request.form.get('cost_limit')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET cost_limit = %s", [cost_limit])
    mysql.connection.commit()
    session['isLimitSet'] = 1
    return redirect('/')


@app.route('/signup', methods=["POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, generate_password_hash(password)))
        mysql.connection.commit()
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
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET name = %s, email = %s, password = %s WHERE user_id = %s", [name, email, generate_password_hash(password), session.get('user_id')])
    mysql.connection.commit()

    return redirect('/')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template('apology.html')


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


@app.route('/populate')
def populate():
    cur = mysql.connection.cursor()
    cur.execute("CREATE TABLE `appliances` (`app_id` int(11) NOT NULL, `user_id` int(11) NOT NULL, `name` varchar(255) NOT NULL, `type` varchar(255) NOT NULL, `power` float NOT NULL, `duration` float NOT NULL, `frequency` varchar(255) NOT NULL, `daily_usage` float NOT NULL, `monthly_usage` float NOT NULL, `daily_cost` float NOT NULL, `monthly_cost` float NOT NULL, `created_at` timestamp NOT NULL DEFAULT current_timestamp(), `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp())")
    mysql.connection.commit()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO `appliances` (`app_id`, `user_id`, `name`, `type`, `power`, `duration`, `frequency`, `daily_usage`, `monthly_usage`, `daily_cost`, `monthly_cost`, `created_at`, `updated_at`) VALUES (1, 2, 'AC', 'Cooling', 4, 4, 'Daily', 0.02, 0.48, 0.18, 5.43, '2021-01-05 14:47:58', '2021-01-05 14:47:58'), (2, 2, 'Bulb', 'Lighting', 5, 8, 'Daily', 0.04, 1.2, 0.45, 13.58, '2021-01-05 14:49:18', '2021-01-05 14:49:18'), (4, 2, 'Computer', 'Entertainment', 10, 18, 'Daily', 0.18, 5.4, 2.04, 61.13, '2021-01-05 14:50:50', '2021-01-05 14:50:50'), (9, 2, 'Rice cooker', 'Kitchen Appliances', 100, 26, 'Daily', 2.6, 78, 29.43, 882.96, '2021-01-07 06:08:55', '2021-01-07 06:08:55'), (10, 2, 'Vacuum', 'Household Appliances', 120, 24, 'Daily', 2.88, 86.4, 32.6, 978.05, '2021-01-07 06:09:38', '2021-01-07 06:09:38'), (12, 2, 'TV', 'Entertainment', 12, 7, 'Daily', 0.08, 2.52, 0.91, 28.53, '2021-01-07 06:22:18', '2021-01-07 06:22:18'), (13, 2, 'TV', 'Entertainment', 12, 7, 'Daily', 0.08, 2.52, 0.91, 28.53, '2021-01-07 06:22:18', '2021-01-07 06:22:18'), (14, 2, 'Fan', 'Cooling', 12, 12, 'Weekly', 0.02, 0.58, 0.23, 6.57, '2021-01-07 06:22:32', '2021-01-07 06:22:32'), (15, 3, 'Smart TV', 'Entertainment', 10, 12, 'Daily', 0.12, 3.6, 1.36, 40.75, '2021-01-07 06:28:50', '2021-01-07 06:28:50');")
    mysql.connection.commit()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute("CREATE TABLE `users` (`user_id` int(11) NOT NULL, `name` varchar(255) NOT NULL, `email` varchar(255) NOT NULL, `password` varchar(255) NOT NULL, `cost_limit` float NOT NULL DEFAULT 1000, `created_at` timestamp NOT NULL DEFAULT current_timestamp(), `updated_at` timestamp NULL DEFAULT current_timestamp()) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    mysql.connection.commit()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO `users` (`user_id`, `name`, `email`, `password`, `cost_limit`, `created_at`, `updated_at`) VALUES (2, 'Arya Stark', 'arya@gmail.com', 'pbkdf2:sha256:150000$Tx8lc70a$9724dab7d3e076da0b0a0a87fc46c9534a8755443f70ce6c505f43db9aa75858', 1000, '2021-01-05 10:50:06', '2021-01-05 10:50:06'), (3, 'Gabriela Balisacan', 'gab@gmail.com', 'pbkdf2:sha256:150000$qXtLW8gr$cbdd3f0772fad9173053a145cd4c5690e36e44488685f7cfa9c9445c45b9f20b',1000, '2021-01-07 06:26:34', '2021-01-07 06:26:34');")
    mysql.connection.commit()
    cur.close()




if __name__ == "__main__":
    app.run(debug=True)