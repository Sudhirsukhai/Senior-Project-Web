from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)


app = Flask(__name__)
app.secret_key = 'supersecretkey'
DB = 'users.db'

# Initialize SQLite DB
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Home route redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)

        try:
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
            user = c.fetchone()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash("Login successful.", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))

    return render_template('index.html')

# Dashboard (protected)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    return f"<h1>Welcome, {session['username']}!</h1><a href='/logout'>Logout</a>"

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))






def calculate_bmr(gender: str, age: int, height_cm: float, weight_kg: float) -> float:
    if gender.lower() == 'male':
        return 66.5 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.75 * age)
    elif gender.lower() == 'female':
        return 655.1 + (9.563 * weight_kg) + (1.850 * height_cm) - (4.676 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'")

def calculate_tdee(bmr: float, activity_level: str) -> float:
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'super': 1.9
    }
    return bmr * multipliers.get(activity_level, 1.2)

@app.route('/bmr', methods=['GET', 'POST'])
def bmr_page():
    bmr = tdee = None
    if request.method == 'POST':
        gender = request.form['gender']
        age = int(request.form['age'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        activity_level = request.form['activity']

        bmr = round(calculate_bmr(gender, age, height, weight), 2)
        tdee = round(calculate_tdee(bmr, activity_level), 2)

    return render_template('CalTrack.html', bmr=bmr, tdee=tdee)

 
if __name__ == '__main__':
    init_db()
    app.run(debug=True)